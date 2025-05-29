"""
Handles loading and inference for a local Hunyuan3D model.
"""
__all__ = ["Local2DTo3DConverter"]

import os
from hy3dgen.shapegen.pipelines import Hunyuan3DDiTFlowMatchingPipeline

class Local2DTo3DConverter:
    """
    Handles loading and inference for a local Hunyuan3D model.

    Parameters
    ----------
    model_dir : str
        Path to the directory containing the model files.
    logger : logging.Logger, optional
        Logger instance for logging events and warnings.
    """
    def __init__(self, model_dir, logger=None):
        """
        Initialize the Local2DTo3DConverter.

        Parameters
        ----------
        model_dir : str
            Path to the directory containing the model files.
        logger : logging.Logger, optional
            Logger instance for logging events and warnings.
        """
        self.logger = logger
        self.pipeline = None
        self.model_dir = model_dir
        self._load_pipeline()

    def _load_pipeline(self):
        """
        Attempt to load the Hunyuan3D pipeline from the local model directory.
        Logs a warning if the model cannot be loaded.
        """
        try:
            abs_model_dir = os.path.abspath(self.model_dir)
            self.pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
                abs_model_dir, local_files_only=True
            )
        except Exception as e:
            msg = f"Hunyuan3D model not loaded: {e}"
            if self.logger:
                self.logger.warning(msg)
            else:
                print(f"Warning: {msg}")

    def convert(self, image_path):
        """
        Convert a 2D image to a 3D mesh using the local pipeline.
        If the model is not loaded, log a warning and return None.

        Parameters
        ----------
        image_path : str
            Path to the input image file.

        Returns
        -------
        mesh : trimesh.Trimesh or None
            The generated 3D mesh object, or None if model is not loaded.
        """
        if self.pipeline is None:
            msg = "2D-to-3D conversion requested but model is not loaded."
            if self.logger:
                self.logger.warning(msg)
            else:
                print(f"Warning: {msg}")
            return None
        mesh = self.pipeline(image=image_path)[0]
        return mesh
