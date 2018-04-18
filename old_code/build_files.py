import argparse
import ConfigParser
import os
from distutils.dir_util import mkpath

import builder
from builder.skeleton import skeleton_handler
from helpers import common_utils

def load_config(config_path): 
	config_load = ConfigParser.ConfigParser()
	config_load.readfp(open(config_path))

	return config_load

def find_skeleton(component_type, component_name):
	return_path = ""
	components_dir = "skeletons" + os.sep + component_type + "s" + os.sep + component_name.replace((component_type + "_"), "") + os.sep
	for subdir, dirs, files in os.walk(components_dir):
		for file in files:
			filepath = components_dir + file
			if component_name in filepath:
				return_path = filepath
	return return_path

def dump_module(filepath):
	fp = open(filepath, 'rb')
	mod_contents = fp.read()
	fp.close()

	return mod_contents

def find_framework(component_type, framework_name):
	filepath = ""
	return_path = []
	components_dir = "skeletons" + os.sep + component_type + "s" + os.sep + framework_name + os.sep
	for subdir, dirs, files in os.walk(components_dir):
		for file in files:
			filepath = subdir + os.sep + file
			if not filepath.endswith(".md"):
				return_path.append(filepath)
	return return_path

def build_framework(build, encoder_path, transport_path):
	framework_files = find_framework("framework", build.framework)
	encoder_code = dump_module(encoder_path)
	transport_code = dump_module(transport_path)
	config.set('framework_options', 'encoder', build.encoder)
	config.set('framework_options', 'transport', build.transport)
	return_paths = []
	for file in framework_files:
		build_skeleton = skeleton_handler.SkeletonHandler(file)
		if args.verbose:
			print "Current framework file: %s" %(file)
		build_skeleton.LoadSkeleton()

		framework_options_str = "framework_options"

		for item in config.items(framework_options_str):
			key = item[0]
			value = item[1]
			build_skeleton.target_var = key
			build_skeleton.regex_replacement_value_marker = '```\[var:::'+build_skeleton.target_var+'\]```'
			build_skeleton.new_value = value
			build_skeleton.ReplaceString()

		for item in [('encoder_code', encoder_code), ('transport_code', transport_code)]:
			key = item[0]
			value = item[1]
			build_skeleton.target_var = key
			build_skeleton.regex_replacement_value_marker = '```\[var:::'+build_skeleton.target_var+'\]```'
			build_skeleton.new_value = value
			build_skeleton.ReplaceString(raw=True)

		file_destination = file.replace(("skeletons" + os.sep), (args.build_path + os.sep))
		mkpath(os.path.dirname(file_destination))

		build.build_client_file(build_skeleton.GetCurrentFile(), file_destination)
		return_paths.append(file_destination)
		
	return return_paths


def build_module(build, module_type, selected_module):
	component_skeleton = find_skeleton(module_type, str(selected_module).strip('"').strip("'"))
	build_skeleton = skeleton_handler.SkeletonHandler(component_skeleton)
	if args.verbose:
		print "CURRENT TARGET SKELETON: " + build_skeleton.target_skeleton
	build_skeleton.LoadSkeleton()

	# if args.debug:
	# 	print "Current %s contents, before loop: " + "\n" + build_skeleton.GetCurrentFile() %(module_type)
	mod_options_str = str(module_type) + "_options"

	for item in config.items(mod_options_str):
		key = item[0]
		value = item[1]
		build_skeleton.target_var = key
		build_skeleton.regex_replacement_value_marker = '```\[var:::'+build_skeleton.target_var+'\]```'
		build_skeleton.new_value = value
		build_skeleton.ReplaceString()
		# if args.debug:
		# 	print "Current %s contents, after loop: " + "\n" + build_skeleton.GetCurrentFile() %(module_type)
	module_destination = args.build_path + os.sep + module_type + os.sep
	mkpath(module_destination)
	module_destination = module_destination + selected_module + ".py"
	build.build_client_file(build_skeleton.GetCurrentFile(), module_destination)
	# Just cleanup
	del build_skeleton, component_skeleton

	return module_destination


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output', dest='verbose', default=False)
	parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging output', dest='debug', default=False)
	parser.add_argument('-f', '--framework', help='The name of the framework to build for', dest='selected_framework')
	parser.add_argument('-e', '--encoder', help='The name of the encoder module to use for the client', dest='selected_encoder')
	parser.add_argument('-t', '--transport', help='The name of the transport module to use for the client', dest='selected_transport')
	parser.add_argument('-c', '--config', help='the/path/to/the/config file to use for the builder routine', dest='config_path')
	parser.add_argument('-b', '--buildpath', help='the/path/to place the built files into', dest='build_path')

	global args
	args = parser.parse_args()

	# Let's load our config file
	global config
	config = load_config(args.config_path)

	# Create the builder object
	build = builder.Builder()

	if not args.selected_framework:
		args.selected_framework = config.get('framework', 'framework')

	# Let's assign the proper builder variables
	build.encoder = str(args.selected_encoder)
	build.transport = str(args.selected_transport)
	build.framework = str(args.selected_framework)
	build.build_path = str(args.build_path)

	# Run any tasks required to prepare the builder before hand.
	build.prep_builder()

	print "Building file(s) for %s, with %s and %s at %s" %(args.selected_framework, args.selected_transport, args.selected_encoder, args.build_path)

	built_encoder_path = build_module(build, "encoder", build.encoder)
	built_transport_path = build_module(build, "transport", build.transport)

	# TODO: For the framework object, we need to recreate the directory structure in the 'build_path',
	#   then iterate through each file in the client for all client_options vars,
	#    then iterate through each file in the server for all server_options vars,
	#     then iterate through each file in both for all framework_options vars
	# Generally, we won't need more than just the framework_options, so we'll start with that...
	built_framework_path = build_framework(build, built_encoder_path, built_transport_path)




main()
