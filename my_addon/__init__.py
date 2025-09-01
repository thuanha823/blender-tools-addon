import importlib
import sys

bl_info = {
    "name": "Custom Tool Addon",
    "author": "Thuan Ha",
    "version": (1, 0, 0),
    "blender": (4, 5, 1),
    "location": "View3D > UI",
    "description": "Custom tools for workflow and convenience",
    "category": "Tools"
}


modules = [
    f"{__name__}.{module}"
    for module in [
        "addon_ui",
        "mirror_tool",
    ]
]


def register():
    for module in modules:
        if module in sys.modules:
            importlib.reload(sys.modules[module])

            if hasattr(sys.modules[module], "register"):
                sys.modules[module].register()

            print('reloaded module "{}"'.format(module))
        else:
            globals()[module] = importlib.import_module(module)

            if hasattr(globals()[module], "register"):
                globals()[module].register()

            print('imported module "{}"'.format(module))


def unregister():
    for module in modules:
        if module not in sys.modules or not hasattr(sys.modules[module], "unregister"):
            continue

        sys.modules[module].unregister()
        print('unregistered module "{}"'.format(module))


if __name__ == "__main__":
    register()