from setuptools import setup

requires = [
    'requests',
    'keyring',
]

setup(
    name="gnome-shell-search-pinboard",
    version='1.0.0',
    description="A gnome shell search provider for your pinboard.in account",
    url="http://github.com/ralphbean/gnome-shell-search-pinboard",
    author="Ralph Bean",
    author_email="rbean@redhat.com",
    license='GPLv3',
    install_requires=requires,
    packages=['gs_search_pinboard'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'gnome-shell-search-pinboard-daemon = gs_search_pinboard.daemon:main',
            'gnome-shell-search-pinboard-config = gs_search_pinboard.popup:main',
        ],
    }
)
