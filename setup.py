import pathlib

from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(name="pyhalboy",
      version="1.0.0",
      description="HALBoy port to python for everything HAL related",
      author="Bamdad Dashtban",
      license="MIT",
      long_description=README,
      setup_requires=["requests",
                      "requests-mock",
                      "ramda",
                      "uritemplate"], pbr=True,
      long_description_content_type="text/markdown",
      packages=find_packages(where="pyhalboy"))
