from setuptools import setup, find_packages

setup(setup_requires=["requests"
                      "requests-mock"
                      "ramda"
                      "uritemplate"], pbr=True,
      packages=find_packages(where="src"))