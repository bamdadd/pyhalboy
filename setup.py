import pathlib

from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(name="pyhalboy",
      version="1.0.3",
      description="HALBoy port to python for everything HAL related",
      author="Bamdad Dashtban",
      license="MIT",
      long_description=README,
      install_requires=["requests",
                      "ramda",
                      "uri",
                      "uritemplate"],
      setup_requires=["requests",
                      "requests-mock",
                      "ramda",
                      "uri",
                      "uritemplate",
                      "pytest"], pbr=True,
      long_description_content_type="text/markdown",
      packages=['pyhalboy'],
      package_dir={'pyhalboy': 'src/pyhalboy'}

      )
