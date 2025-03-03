from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.units import inch
import importlib

def load_logo(width=3*inch):
    # Get the directory of the current file (images.py)
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # image_path = os.path.join(current_dir, image_path)  # Combine it with the image name
    
    with importlib.resources.path('lyik.components','logo.png') as w2w_logo_path:
        img = ImageReader(w2w_logo_path)
        img_w, img_h = img.getSize()
        return Image(w2w_logo_path, width=width, height=img_h * width / img_w)  # Adjust size as needed