from flask import Blueprint, request, send_file, jsonify
import tempfile
import os
from src.utils.configuration import ConfigLoader
from src.utils.local_2d_to_3d import Local2DTo3DConverter

class ConvertAPI:
    """
    API class for 2D to 3D model conversion endpoints.

    Parameters
    ----------
    logger : logging.Logger
        Logger instance for logging API events.
    config : ConfigLoader
        Configuration loader instance for model and output settings.
    """
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.api = Blueprint('api', __name__)
        self.converter = self.load_converter()
        self.add_routes()

    def load_converter(self):
        """
        Load and return the 2D to 3D conversion utility using the correct model path.
        If the model is not loaded, log a warning.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(base_dir)
        parent_parent_dir = os.path.dirname(parent_dir)
        model_dir_name = self.config.get('model_name')
        model_dir = os.path.join(parent_parent_dir, 'models', model_dir_name)
        converter = Local2DTo3DConverter(model_dir, logger=self.logger)
        if converter.pipeline is None:
            self.logger.warning("2D-to-3D conversion requested but model is not loaded.")
            return None
        return converter


    def add_routes(self):
        @self.api.route('/convert', methods=['POST'])
        def convert_2d_to_3d():
            """
            Convert a 2D image to a 3D model (.obj) and return the file.

            Returns
            -------
            flask.Response
                The generated .obj file as a downloadable response, or error JSON.
            """
            if 'image' not in request.files:
                self.logger.warning('Missing image file in request')
                return jsonify({'error': 'Missing image file in request'}), 400

            image_file = request.files['image']
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_img:
                image_file.save(temp_img.name)
                temp_img_path = temp_img.name

            try:
                # Use the utility class for conversion
                converter = self.converter
                if converter is None:
                    return jsonify({
                        'error': '3D model conversion is not available: model is not loaded.'
                    }), 503
                mesh = converter.convert(temp_img_path)
                if mesh is None:
                    return jsonify({
                        'error': '3D model conversion is not available: model is not loaded.'
                    }), 503
                output_format = self.config.get('output_format', 'obj')
                output_filename = self.config.get('output_filename', 'model.obj')
                output_mimetype = self.config.get('output_mimetype', 'text/plain')
                with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format}') as obj_file:
                    mesh.export(obj_file.name)
                    obj_path = obj_file.name
            except Exception as e:
                self.logger.error(f'Error during 2D to 3D conversion: {e}')
                os.remove(temp_img_path)
                return jsonify({
                    'error': 'Failed to generate 3D model',
                    'details': str(e)
                }), 500

            self.logger.info('2D image converted to 3D model and returned as .obj')
            response = send_file(
                obj_path,
                as_attachment=True,
                download_name=output_filename,
                mimetype=output_mimetype
            )

            @response.call_on_close
            def cleanup():
                os.remove(temp_img_path)
                os.remove(obj_path)

            return response