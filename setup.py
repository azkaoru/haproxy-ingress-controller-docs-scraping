from setuptools import setup, find_packages


setup(
    name='jrnote',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pyyaml',"lxml"
    ],
    include_pacakge_date=True,
    entry_points="""
        [console_scripts]
        main = jrnote:main
    """,
)
