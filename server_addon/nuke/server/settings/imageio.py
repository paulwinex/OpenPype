from typing import Literal
from pydantic import validator, Field
from ayon_server.settings import (
    BaseSettingsModel,
    ensure_unique_names,
)

from .common import KnobModel


class NodesModel(BaseSettingsModel):
    _layout = "expanded"
    plugins: list[str] = Field(
        default_factory=list,
        title="Used in plugins"
    )
    nuke_node_class: str = Field(
        title="Nuke Node Class",
    )


class RequiredNodesModel(NodesModel):
    knobs: list[KnobModel] = Field(
        default_factory=list,
        title="Knobs",
    )

    @validator("knobs")
    def ensure_unique_names(cls, value):
        """Ensure name fields within the lists have unique names."""
        ensure_unique_names(value)
        return value


class OverrideNodesModel(NodesModel):
    subsets: list[str] = Field(
        default_factory=list,
        title="Subsets"
    )

    knobs: list[KnobModel] = Field(
        default_factory=list,
        title="Knobs",
    )

    @validator("knobs")
    def ensure_unique_names(cls, value):
        """Ensure name fields within the lists have unique names."""
        ensure_unique_names(value)
        return value


class NodesSetting(BaseSettingsModel):
    required_nodes: list[RequiredNodesModel] = Field(
        title="Plugin required",
        default_factory=list
    )
    override_nodes: list[OverrideNodesModel] = Field(
        title="Plugin's node overrides",
        default_factory=list
    )


def ocio_configs_switcher_enum():
    return [
        {"value": "nuke-default", "label": "nuke-default"},
        {"value": "spi-vfx", "label": "spi-vfx (11)"},
        {"value": "spi-anim", "label": "spi-anim (11)"},
        {"value": "aces_0.1.1", "label": "aces_0.1.1 (11)"},
        {"value": "aces_0.7.1", "label": "aces_0.7.1 (11)"},
        {"value": "aces_1.0.1", "label": "aces_1.0.1 (11)"},
        {"value": "aces_1.0.3", "label": "aces_1.0.3 (11, 12)"},
        {"value": "aces_1.1", "label": "aces_1.1 (12, 13)"},
        {"value": "aces_1.2", "label": "aces_1.2 (13, 14)"},
        {"value": "studio-config-v1.0.0_aces-v1.3_ocio-v2.1",
         "label": "studio-config-v1.0.0_aces-v1.3_ocio-v2.1 (14)"},
        {"value": "cg-config-v1.0.0_aces-v1.3_ocio-v2.1",
         "label": "cg-config-v1.0.0_aces-v1.3_ocio-v2.1 (14)"},
    ]


class WorkfileColorspaceSettings(BaseSettingsModel):
    """Nuke workfile colorspace preset. """

    color_management: Literal["Nuke", "OCIO"] = Field(
        title="Color Management Workflow"
    )

    native_ocio_config: str = Field(
        title="Native OpenColorIO Config",
        description="Switch between native OCIO configs",
        enum_resolver=ocio_configs_switcher_enum,
        conditionalEnum=True
    )

    working_space: str = Field(
        title="Working Space"
    )
    thumbnail_space: str = Field(
        title="Thumbnail Space"
    )


class ReadColorspaceRulesItems(BaseSettingsModel):
    _layout = "expanded"

    regex: str = Field("", title="Regex expression")
    colorspace: str = Field("", title="Colorspace")


class RegexInputsModel(BaseSettingsModel):
    inputs: list[ReadColorspaceRulesItems] = Field(
        default_factory=list,
        title="Inputs"
    )


class ViewProcessModel(BaseSettingsModel):
    viewerProcess: str = Field(
        title="Viewer Process Name"
    )


class ImageIOConfigModel(BaseSettingsModel):
    override_global_config: bool = Field(
        False,
        title="Override global OCIO config"
    )
    filepath: list[str] = Field(
        default_factory=list,
        title="Config path"
    )


class ImageIOFileRuleModel(BaseSettingsModel):
    name: str = Field("", title="Rule name")
    pattern: str = Field("", title="Regex pattern")
    colorspace: str = Field("", title="Colorspace name")
    ext: str = Field("", title="File extension")


class ImageIOFileRulesModel(BaseSettingsModel):
    activate_host_rules: bool = Field(False)
    rules: list[ImageIOFileRuleModel] = Field(
        default_factory=list,
        title="Rules"
    )

    @validator("rules")
    def validate_unique_outputs(cls, value):
        ensure_unique_names(value)
        return value


class ImageIOSettings(BaseSettingsModel):
    """Nuke color management project settings. """
    _isGroup: bool = True

    """# TODO: enhance settings with host api:
    to restructure settings for simplification.

    now: nuke/imageio/viewer/viewerProcess
    future: nuke/imageio/viewer
    """
    activate_host_color_management: bool = Field(
        True, title="Enable Color Management")
    ocio_config: ImageIOConfigModel = Field(
        default_factory=ImageIOConfigModel,
        title="OCIO config"
    )
    file_rules: ImageIOFileRulesModel = Field(
        default_factory=ImageIOFileRulesModel,
        title="File Rules"
    )
    viewer: ViewProcessModel = Field(
        default_factory=ViewProcessModel,
        title="Viewer",
        description="""Viewer profile is used during
        Creation of new viewer node at knob viewerProcess"""
    )

    """# TODO: enhance settings with host api:
    to restructure settings for simplification.

    now: nuke/imageio/baking/viewerProcess
    future: nuke/imageio/baking
    """
    baking: ViewProcessModel = Field(
        default_factory=ViewProcessModel,
        title="Baking",
        description="""Baking profile is used during
        publishing baked colorspace data at knob viewerProcess"""
    )

    workfile: WorkfileColorspaceSettings = Field(
        default_factory=WorkfileColorspaceSettings,
        title="Workfile"
    )

    nodes: NodesSetting = Field(
        default_factory=NodesSetting,
        title="Nodes"
    )
    """# TODO: enhance settings with host api:
    - [ ] no need for `inputs` middle part. It can stay
      directly on `regex_inputs`
    """
    regex_inputs: RegexInputsModel = Field(
        default_factory=RegexInputsModel,
        title="Assign colorspace to read nodes via rules"
    )


DEFAULT_IMAGEIO_SETTINGS = {
    "viewer": {
        "viewerProcess": "sRGB"
    },
    "baking": {
        "viewerProcess": "rec709"
    },
    "workfile": {
        "color_management": "Nuke",
        "native_ocio_config": "nuke-default",
        "working_space": "linear",
        "thumbnail_space": "sRGB",
    },
    "nodes": {
        "required_nodes": [
            {
                "plugins": [
                    "CreateWriteRender"
                ],
                "nuke_node_class": "Write",
                "knobs": [
                    {
                        "type": "text",
                        "name": "file_type",
                        "text": "exr"
                    },
                    {
                        "type": "text",
                        "name": "datatype",
                        "text": "16 bit half"
                    },
                    {
                        "type": "text",
                        "name": "compression",
                        "text": "Zip (1 scanline)"
                    },
                    {
                        "type": "boolean",
                        "name": "autocrop",
                        "boolean": True
                    },
                    {
                        "type": "color_gui",
                        "name": "tile_color",
                        "color_gui": [
                            186,
                            35,
                            35
                        ]
                    },
                    {
                        "type": "text",
                        "name": "channels",
                        "text": "rgb"
                    },
                    {
                        "type": "text",
                        "name": "colorspace",
                        "text": "linear"
                    },
                    {
                        "type": "boolean",
                        "name": "create_directories",
                        "boolean": True
                    }
                ]
            },
            {
                "plugins": [
                    "CreateWritePrerender"
                ],
                "nuke_node_class": "Write",
                "knobs": [
                    {
                        "type": "text",
                        "name": "file_type",
                        "text": "exr"
                    },
                    {
                        "type": "text",
                        "name": "datatype",
                        "text": "16 bit half"
                    },
                    {
                        "type": "text",
                        "name": "compression",
                        "text": "Zip (1 scanline)"
                    },
                    {
                        "type": "boolean",
                        "name": "autocrop",
                        "boolean": True
                    },
                    {
                        "type": "color_gui",
                        "name": "tile_color",
                        "color_gui": [
                            171,
                            171,
                            10
                        ]
                    },
                    {
                        "type": "text",
                        "name": "channels",
                        "text": "rgb"
                    },
                    {
                        "type": "text",
                        "name": "colorspace",
                        "text": "linear"
                    },
                    {
                        "type": "boolean",
                        "name": "create_directories",
                        "boolean": True
                    }
                ]
            },
            {
                "plugins": [
                    "CreateWriteImage"
                ],
                "nuke_node_class": "Write",
                "knobs": [
                    {
                        "type": "text",
                        "name": "file_type",
                        "text": "tiff"
                    },
                    {
                        "type": "text",
                        "name": "datatype",
                        "text": "16 bit"
                    },
                    {
                        "type": "text",
                        "name": "compression",
                        "text": "Deflate"
                    },
                    {
                        "type": "color_gui",
                        "name": "tile_color",
                        "color_gui": [
                            56,
                            162,
                            7
                        ]
                    },
                    {
                        "type": "text",
                        "name": "channels",
                        "text": "rgb"
                    },
                    {
                        "type": "text",
                        "name": "colorspace",
                        "text": "sRGB"
                    },
                    {
                        "type": "boolean",
                        "name": "create_directories",
                        "boolean": True
                    }
                ]
            }
        ],
        "override_nodes": []
    },
    "regex_inputs": {
        "inputs": [
            {
                "regex": "(beauty).*(?=.exr)",
                "colorspace": "linear"
            }
        ]
    }
}
