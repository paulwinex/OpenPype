import os
from copy import deepcopy
import opentimelineio as otio
from openpype.client import get_asset_by_name
from openpype.hosts.traypublisher.api.plugin import TrayPublishCreator
from openpype.pipeline.create.creator_plugins import InvisibleCreator

from openpype.pipeline import CreatedInstance

from openpype.lib import (
    FileDef,
    TextDef,
    NumberDef,
    EnumDef,
    BoolDef
)

from openpype.hosts.traypublisher.api.pipeline import HostContext


class EditorialClipInstanceCreator(InvisibleCreator):
    identifier = "editorial.clip"
    family = "clip"
    host_name = "traypublisher"

    def __init__(
        self, create_context, system_settings, project_settings,
        *args, **kwargs
    ):
        super(EditorialClipInstanceCreator, self).__init__(
            create_context, system_settings, project_settings, *args, **kwargs
        )

    def create(self, instance_data, source_data):
        # instance_data > asset, task_name, variant, family
        # source_data > additional data
        self.log.info(f"instance_data: {instance_data}")
        self.log.info(f"source_data: {source_data}")


class EditorialSimpleCreator(TrayPublishCreator):

    label = "Editorial Simple"
    family = "editorial"
    identifier = "editorial.simple"
    default_variants = [
        "main",
        "review"
    ]
    description = "Editorial files to generate shots."
    detailed_description = """
Supporting publishing new shots to project
or updating already created. Publishing will create OTIO file.
"""
    icon = "fa.file"

    def __init__(
        self, create_context, system_settings, project_settings,
        *args, **kwargs
    ):
        super(EditorialSimpleCreator, self).__init__(
            create_context, system_settings, project_settings, *args, **kwargs
        )
        editorial_creators = (
            project_settings["traypublisher"]["editorial_creators"]
        )
        self._editorial_creators = deepcopy(editorial_creators)

    def create(self, subset_name, instance_data, pre_create_data):
        # TODO: create otio instance
        asset_name = instance_data["asset"]
        asset_doc = get_asset_by_name(self.project_name, asset_name)
        otio_timeline = self._create_otio_instance(
            subset_name, instance_data, pre_create_data)

        # TODO: create clip instances
        editorial_clip_creator = self.create_context.creators["editorial.clip"]
        editorial_clip_creator.create({}, {})

    def _create_otio_instance(self, subset_name, data, pre_create_data):
        # from openpype import lib as plib

        # get path of sequence
        file_path_data = pre_create_data["sequence_filepath_data"]
        file_path = os.path.join(
            file_path_data["directory"], file_path_data["filenames"][0])

        self.log.info(f"file_path: {file_path}")

        # get editorial sequence file into otio timeline object
        extension = os.path.splitext(file_path)[1]
        kwargs = {}
        if extension == ".edl":
            # EDL has no frame rate embedded so needs explicit
            # frame rate else 24 is asssumed.
            kwargs["rate"] = float(25)
            # plib.get_asset()["data"]["fps"]

        self.log.info(f"kwargs: {kwargs}")
        otio_timeline = otio.adapters.read_from_file(
            file_path, **kwargs)

        # Pass precreate data to creator attributes
        data.update({
            "creator_attributes": pre_create_data,
            "editorial_creator": True

        })

        self._create_instance(self.family, subset_name, data)

        return otio_timeline

    def _create_instance(self, family, subset_name, data):
        # Create new instance
        new_instance = CreatedInstance(family, subset_name, data, self)
        # Host implementation of storing metadata about instance
        HostContext.add_instance(new_instance.data_to_store())
        # Add instance to current context
        self._add_instance_to_context(new_instance)

    def get_instance_attr_defs(self):
        return [
            FileDef(
                "sequence_filepath_data",
                folders=False,
                extensions=[
                    ".edl",
                    ".xml",
                    ".aaf",
                    ".fcpxml"
                ],
                allow_sequences=False,
                label="Filepath",
            )
        ]
