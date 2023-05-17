import os
import pyblish.api
from openpype.pipeline import publish, OptionalPyblishPluginMixin
from pymxs import runtime as rt
from openpype.hosts.max.api import maintained_selection, get_all_children


class ExtractCameraAlembic(publish.Extractor, OptionalPyblishPluginMixin):
    """
    Extract Camera with AlembicExport
    """

    order = pyblish.api.ExtractorOrder - 0.1
    label = "Extract Alembic Camera"
    hosts = ["max"]
    families = ["camera"]
    optional = True

    def process(self, instance):
        if not self.is_active(instance.data):
            return
        start = float(instance.data.get("frameStartHandle", 1))
        end = float(instance.data.get("frameEndHandle", 1))

        container = instance.data["instance_node"]

        self.log.info("Extracting Camera ...")

        stagingdir = self.staging_dir(instance)
        filename = "{name}.abc".format(**instance.data)
        path = os.path.join(stagingdir, filename)

        # We run the render
        self.log.info("Writing alembic '%s' to '%s'" % (filename, stagingdir))

        rt.AlembicExport.ArchiveType = rt.name("ogawa")
        rt.AlembicExport.CoordinateSystem = rt.name("maya")
        rt.AlembicExport.StartFrame = start
        rt.AlembicExport.EndFrame = end
        rt.AlembicExport.CustomAttributes = True

        with maintained_selection():
            # select and export
            rt.select(get_all_children(rt.getNodeByName(container)))
            rt.exportFile(path, selectedOnly=True, using="AlembicExport", noPrompt=True)

        self.log.info("Performing Extraction ...")
        if "representations" not in instance.data:
            instance.data["representations"] = []

        representation = {
            "name": "abc",
            "ext": "abc",
            "files": filename,
            "stagingDir": stagingdir,
        }
        instance.data["representations"].append(representation)
        self.log.info("Extracted instance '%s' to: %s" % (instance.name, path))
