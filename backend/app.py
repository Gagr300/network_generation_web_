import os
import json
import time
import threading
import traceback
import uuid
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import tempfile
import networkx as nx
from network_generation.triplet_model import RandomGraphGenerator, motifs
from network_generation.utils import graph_to_json, calculate_graph_metrics
from flask import Response

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

progress_data = {}


@app.route('/api/generate_stream', methods=['POST'])
def generate_graph_stream():
    """Генерация графа с потоковым обновлением прогресса через WebSocket"""
    data = request.json
    original_graph = data.get('original_graph')
    session_id = data.get('session_id') or str(uuid.uuid4())
    num_nodes_in_motif = data.get('num_nodes_in_motif', 3)  # количество вершин в мотиве
    new_nodes_number = data.get('new_nodes_number')  # количество вершин в новом графе
    probability_type = data.get('probability_type', 0)  # способ вычисления вероятности
    probability_type_map = {
        0: 'frequency',
        1: 'laplace',
        2: 'soft-max'
    }
    probability_type = probability_type_map.get(probability_type, 'frequency')

    if not original_graph:
        return jsonify({'error': 'No graph data provided'}), 400

    N = len(original_graph['nodes'])
    M = len(original_graph['edges'])

    total_edges = int(M * (new_nodes_number / N)) if new_nodes_number else M

    progress_data[session_id] = {
        'progress': 0,
        'current': 0,
        'total': 0,
        'status': 'starting',
        'num_nodes_in_motif': num_nodes_in_motif,
        'new_nodes_number': new_nodes_number
    }

    # начальный статус
    socketio.emit('generation_progress', {
        'session_id': session_id,
        'progress': 0,
        'current': 0,
        'total': 0,
        'status': 'starting',
        'num_nodes_in_motif': num_nodes_in_motif
    })

    # генерация в отдельном потоке
    def generate_in_thread():
        try:
            G = nx.DiGraph()
            for node in original_graph['nodes']:
                G.add_node(node['id'])
            for edge in original_graph['edges']:
                G.add_edge(edge['source'], edge['target'])

            progress_data[session_id].update({
                'total': total_edges,
                'status': 'generating'
            })

            generator = RandomGraphGenerator(G, num_nodes_in_motif)

            def progress_callback(current, total):
                progress = min(100, int((current / total) * 100))
                progress_data[session_id].update({
                    'progress': progress,
                    'current': current,
                    'total': total,
                    'status': 'generating'
                })
                # обновление
                socketio.emit('generation_progress', {
                    'session_id': session_id,
                    'progress': progress,
                    'current': current,
                    'total': total,
                    'status': 'generating',
                    'num_nodes_in_motif': num_nodes_in_motif
                })

            # генерация графа и расчет метрик
            generator.set_progress_callback(progress_callback)
            new_G = generator.wegner_multiplet_model(new_n=new_nodes_number, probability_type=probability_type) \
                if new_nodes_number else generator.wegner_multiplet_model()
            metrics = calculate_graph_metrics(new_G)
            graph_json = graph_to_json(new_G)
            progress_data[session_id]['status'] = 'complete'

            socketio.emit('generation_complete', {
                'session_id': session_id,
                'success': True,
                'metrics': metrics,
                'graph': graph_json,
                'status': 'complete',
                'edges_generated': len(new_G.edges()),
                'edges_target': total_edges,
                'num_nodes_in_motif': num_nodes_in_motif,
                'nodes_generated': len(new_G.nodes())
            })

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Error in generation thread: {error_details}")

            progress_data[session_id]['status'] = 'error'
            socketio.emit('generation_error', {
                'session_id': session_id,
                'error': str(e),
                'details': error_details,
                'status': 'error'
            })
        finally:
            time.sleep(5)
            if session_id in progress_data:
                del progress_data[session_id]

    thread = threading.Thread(target=generate_in_thread, name=f"GenThread-{session_id}")
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Generation started',
        'total_edges': total_edges,
        'num_nodes_in_motif': num_nodes_in_motif,
        'new_nodes_number': new_nodes_number
    })


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('get_progress')
def handle_get_progress(data):
    session_id = data.get('session_id')
    if session_id and session_id in progress_data:
        emit('progress_update', progress_data[session_id])
    else:
        emit('progress_update', {
            'progress': 0,
            'current': 0,
            'total': 0,
            'status': 'not_found'
        })


@app.route('/api/upload', methods=['POST'])
def upload_graph():
    """Загрузка графа из файла"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # чтение загруженного графа и рассчет метрик
    try:
        if file.filename.endswith('.txt'):
            G = nx.read_edgelist(filepath, create_using=nx.DiGraph())
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

        metrics = calculate_graph_metrics(G)

        graph_json = graph_to_json(G)

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


@app.route('/api/analyze', methods=['POST'])
def analyze_graph():
    """Анализ мотивов в графе"""
    data = request.json
    graph_data = data.get('graph')
    num_nodes_in_motif = data.get('num_nodes_in_motif', 3)  # Получаем размер мотива для анализа

    if not graph_data:
        return jsonify({'error': 'No graph data provided'}), 400

    try:
        G = nx.DiGraph()
        for node in graph_data['nodes']:
            G.add_node(node['id'])
        for edge in graph_data['edges']:
            G.add_edge(edge['source'], edge['target'])

        # анализ мотивов с указанным размером
        generator = RandomGraphGenerator(G, num_nodes_in_motif)
        structure = generator.subgraphStructure

        motifs_info = []
        for motif in structure.motif_subgraphs.values():
            motifs_info.append({
                'id': motif.index,
                'count': motif.count,
                'probability': motif.probability
            })

        return jsonify({
            'success': True,
            'motifs': motifs_info,
            'total_motifs': structure.motifs_sum,
            'num_nodes_in_motif': num_nodes_in_motif
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def download_graph():
    """Скачивание графа в различных форматах"""
    data = request.json
    graph_data = data.get('graph')
    format_type = data.get('format', 'txt')

    print(f"Download request received. Format: {format_type}")

    if not graph_data:
        return jsonify({'error': 'No graph data provided'}), 400

    try:
        # Создаем граф
        G = nx.DiGraph()
        for node in graph_data['nodes']:
            G.add_node(node['id'])
        for edge in graph_data['edges']:
            G.add_edge(edge['source'], edge['target'])

        # Генерируем содержимое в памяти
        if format_type == 'txt':
            content = '\n'.join(f"{edge[0]} {edge[1]}" for edge in G.edges())
            mimetype = 'text/plain'
        elif format_type == 'json':
            import json
            content = json.dumps(graph_to_json(G), indent=2)
            mimetype = 'application/json'
        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400

        return Response(
            content,
            mimetype=mimetype,
            headers={
                'Content-Disposition': f'attachment; filename=graph.{format_type}'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """Получение примера графа"""
    try:
        G = nx.DiGraph({
            1: [2, 3, 8, 9, 10, 14],
            2: [1, 8, 15],
            3: [5, 9, 13],
            4: [2, 11, 15, 7],
            5: [4, 14],
            6: [11, 12, 13, 14],
            7: [6],
            8: [1, 7, 9, 10],
            9: [11],
            10: [2, 4, 6],
            11: [5, 7],
            12: [8, 9],
            13: [1, 2, 5, 9],
            14: [15],
            15: [12]
        })

        metrics = calculate_graph_metrics(G)

        graph_json = graph_to_json(G)

        return jsonify({
            'success': True,
            'metrics': metrics,
            'graph': graph_json
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/')
def serve_index():
    """Главная страница"""
    return send_from_directory(app.static_folder, 'index.html')


# Папка для временных файлов
UPLOAD_FOLDER = tempfile.mkdtemp()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)
