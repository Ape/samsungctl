#!/usr/bin/env python


def clean_eggs(found):
    import site
    import os

    package_locations = site.getsitepackages()
    package_locations += [
        site.getuserbase(),
        site.getusersitepackages()
    ]

    easy_install_locations = []

    for pth in package_locations:
        pth = os.path.join(pth, 'easy_install.pth')
        if os.path.exists(pth):
            easy_install_locations += [pth]

    for loc, ver in found:

        for easy_path in easy_install_locations:
            if os.path.split(easy_path)[0] in loc:
                loc = './' + os.path.split(loc)[-1]
                with open(easy_path, 'r') as f:
                    easy_install_modules = f.read()

                if loc in easy_install_modules:
                    easy_install_modules = (
                        easy_install_modules.replace(loc + '\n', '')
                    )
                    easy_install_modules = (
                        easy_install_modules.replace(loc, '')
                    )

                    with open(easy_path, 'w') as f:
                        f.write('\n'.join(easy_install_modules))


def remove_installs():
    import sys
    import pkg_resources
    import imp
    import os
    import zipimport

    try:
        from pip import main
    except ImportError:
        from pip._internal import main

    found_installs = []

    def is_version_good(v):
        v = tuple(int(i) for i in v.split('.'))
        return v <= (0, 48, 0)

    for dist in pkg_resources.working_set:
        for pkg_name in dist._get_metadata('top_level.txt'):
            if pkg_name == 'websocket':

                for location in sys.path:
                    if location.startswith('/usr'):
                        continue

                    try:
                        fp, path_name, description = imp.find_module(
                            pkg_name,
                            [location]
                        )
                        try:
                            module = imp.load_module(
                                pkg_name,
                                fp,
                                path_name,
                                description
                            )
                        finally:
                            if fp:
                                fp.close()
                    except:
                        if os.path.isfile(location):
                            module = zipimport.zipimporter(
                                location
                            ).find_module(pkg_name)
                        else:
                            continue

                    if module and not is_version_good(module.__version__):
                        if (location, module.__version__) not in found_installs:
                            found_installs += [(location, module.__version__)]

    if found_installs:
        message = (
            'There are {0} version(s) of the websocket-client library that \n'
            'are currently installed that are newer then the one that is \n'
            'needed by samsungctl.\n'
            'There are bugs in the version(s) that are installed that will \n'
            'cause problems with samsungctl.\n\n'
            'Would you like to downgrade the installed version(s) of the \n'
            'websocket-client library (Y/N)?'
        ).format(len(found_installs))

        try:
            answer = raw_input(message)
        except NameError:
            answer = input(message)

        answer = answer.lower()
        if not answer.strip() or answer.strip()[0] != 'y':
            sys.exit(1)

    cleanup = []

    for loc, ver in found_installs:
        if not loc.endswith('.egg'):
            main(['uninstall', 'websocket-client==' + ver])
        else:
            cleanup.append((loc, ver))

    if cleanup:
        clean_eggs(cleanup)


try:
    import websocket
    remove_installs()
except ImportError:
    websocket = None

del websocket

import setuptools # NOQA
import samsungctl # NOQA

setuptools.setup(
    name=samsungctl.__title__,
    version=samsungctl.__version__,
    description=samsungctl.__doc__,
    url=samsungctl.__url__,
    author=samsungctl.__author__,
    author_email=samsungctl.__author_email__,
    license=samsungctl.__license__,
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": ["samsungctl=samsungctl.__main__:main"]
    },
    packages=["samsungctl"],
    install_requires=["websocket-client==0.48.0"],
    extras_require={
        "interactive_ui": ["curses"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
    zip_safe=False
)
