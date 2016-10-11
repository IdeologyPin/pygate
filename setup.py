from setuptools import setup

setup(name='pygate',
      version='0.1.0.dev1',
      description='Python General Architecture for Text Engineering',
      url='https://github.com/IdeologyPin/pygate',
      author='Sasinda',
      author_email='sp2335@cornell.edu',
      license='MIT',
      packages=['pygate'],
      zip_safe=False,
      classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',
            'Topic :: Natural Language Processing :: Framework',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
      ],
      )