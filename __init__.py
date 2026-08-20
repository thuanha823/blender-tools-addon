import importlib
import sys
import bpy
from bpy.props import StringProperty, PointerProperty

bl_info = {
    "name": "Thuan Blender Addon",
    "author": "Thuan Ha",
    "version": (1, 0, 0),
    "blender": (5, 2, 0),
    "location": "View3D > UI",
    "description": "Custom tools for workflow and convenience",
    "category": "Tools"
}


class MyAddonProperties(bpy.types.PropertyGroup):
    # Create folder browser
    export_directory: StringProperty(
        name = "Path",
        description = "Choose an export location",
        default = "",
        subtype = 'DIR_PATH'
    )


modules = [
    f"{__name__}.{module}"
    for module in [
        "addon_ui",
        "tool_general",
        "tool_mirror_tool",
        "tool_index_assign",
    ]
]


def register():
    # Regiser custom properties first
    bpy.utils.register_class(MyAddonProperties)
    bpy.types.Scene.my_addon_props = PointerProperty(type=MyAddonProperties)
    print("Addon properties registered.")
    
    # Loop through sub-modules and register them
    for module_name in modules:
        if module_name in sys.modules:
            module = importlib.reload(sys.modules[module_name])
            print(f'reloaded module "{module_name}"')
        else:
            module = importlib.import_module(module_name)
            print(f'imported module "{module_name}"')
        
        if hasattr(module, "register"):
            module.register()

def unregister():
    # Unregister the sub-modules first
    for module_name in reversed(modules): # Unregister in reverse order
        if module_name in sys.modules and hasattr(sys.modules[module_name], "unregister"):
            sys.modules[module_name].unregister()
            print(f'unregistered module "{module_name}"')
    
    # Unregister custom properties
    del bpy.types.Scene.my_addon_props
    bpy.utils.unregister_class(MyAddonProperties)
    print("Addon properties unregistered.")
    
if __name__ == "__main__":
    register()