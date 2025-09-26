import importlib
import sys
import bpy
from bpy.props import StringProperty, PointerProperty

bl_info = {
    "name": "Custom Tool Addon",
    "author": "Thuan Ha",
    "version": (1, 0, 0),
    "blender": (4, 5, 1),
    "location": "View3D > UI",
    "description": "Custom tools for workflow and convenience",
    "category": "Tools"
}


class MyAddonProperties(bpy.types.PropertyGroup):
    export_filepath: StringProperty(
        name = "Export Path",
        description = "File path for exporting objects",
        subtype = 'FILE_PATH'
    )


modules = [
    f"{__name__}.{module}"
    for module in [
        "addon_ui",
        "mirror_tool",
    ]
]


def register():
    # Loop through sub-modules and register them first
    for module_name in modules:
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
            print(f'reloaded module "{module_name}"')
        else:
            module = importlib.import_module(module_name)
            print(f'imported module "{module_name}"')
        
        if hasattr(module, "register"):
            module.register()
            
    # Then, register the custom properties
    bpy.utils.register_class(MyAddonProperties)
    bpy.types.Scene.my_addon_props = PointerProperty(type=MyAddonProperties)
    
    print("Addon properties registered.")


def unregister():
    # Unregister custom properties first
    del bpy.types.Scene.my_addon_props
    bpy.utils.unregister_class(MyAddonProperties)
    print("Addon properties unregistered.")
    
    # Then, loop through and unregister the sub-modules
    for module_name in reversed(modules): # Unregister in reverse order
        if module_name in sys.modules and hasattr(sys.modules[module_name], "unregister"):
            sys.modules[module_name].unregister()
            print(f'unregistered module "{module_name}"')


if __name__ == "__main__":
    register()