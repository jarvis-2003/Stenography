from flask import Blueprint , request , jsonify,send_file,current_app
from .task import process_image , reverse_image
# from app import create_app

import io



bp = Blueprint('routes',__name__)

@bp.route('/process',methods=['POST'])

def process():
    if 'image' not in request.files or 'text' not in request.form:
        return jsonify({'error': 'Image or text not provided'}), 400

    image_file = request.files['image'].read()
    text = request.form['text']

    
    

    task = process_image.delay(image_file,text)
    return jsonify({'taskid': task.id}),202




@bp.route('/reverse',methods=['POST'])
def reverse():
    if 'imageOg' not in request.files or 'imageOu' not in request.files:
        return jsonify({'error': 'Both original and output images are required'}), 400

    image_og = request.files['imageOg']
    output_image = request.files['imageOu']

    task = reverse_image.delay(image_og.read(),output_image.read())

    return jsonify({'taskid':task.id})



@bp.route('/task_status/<task_id>',methods=['GET'])
def task_status(task_id):
    # from app import celery
    from app import celery


    task = celery.AsyncResult(task_id)


    if task.state == 'PENDING':
        response = {'state': task.state}
    elif task.state == 'SUCCESS':
        result = task.result
        if isinstance(result,bytes):
            return send_file(io.BytesIO(result),mimetype='image/png',as_attachment = True, download_name='output_image.png')
        elif isinstance(result,str):
            return jsonify({'state':task.state, 'message':result})
        
    return jsonify({'state': task.state, 'error': str(task.info)}), 500