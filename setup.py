from setuptools import setup, find_packages

setup(
    name='django-candv-choices',
    version='1.1.0',
    description="Use complex constants built with 'candv' library instead of "
                "standard 'choices' fields for 'Django' models.",
    keywords=[
        'choices', 'constants', 'Django', 'candv', 'values',
    ],
    license='LGPLv3',
    url='https://github.com/oblalex/django-candv-choices',
    author='Alexander Oblovatniy',
    author_email='oblovatniy@gmail.com',
    packages=find_packages(),
    namespace_packages=[
        'candv_x', 'candv_x.django',
    ],
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries',
    ],
)
