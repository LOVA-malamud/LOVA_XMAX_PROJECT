import logging
import os


def setup_logging(log_dir: str = "logs") -> None:
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "xmax_app.log")),
            logging.StreamHandler(),
        ],
    )
