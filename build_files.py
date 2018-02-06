import argparse
import builder
import ConfigParser

def load_config(config_path): 
	config = ConfigParser.ConfigParser()
	config.readfp(open(config_path))

	return config

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument(['-v', '--verbose'], action='store_true', help='Enable verbose output', dest='verbose', default=False)
	parser.add_argument(['-d', '--debug'], action='store_true', help='Enable debugging output', dest='debug', default=False)
	parser.add_argument(['-f', '--framework'], help='The name of the framework to build for', dest='selected_framework')
	parser.add_argument(['-e', '--encoder'], help='The name of the encoder module to use for the client', dest='selected_encoder')
	parser.add_argument(['-t', '--transport'], help='The name of the transport module to use for the client', dest='selected_transport')
	parser.add_argument(['-c', '--config'], help='the/path/to/the/config file to use for the builder routine', dest='config_path')
	parser.add_argument(['-b', '--buildpath'], help='the/path/to place the built files into', dest='build_path')

	args = parser.parse_args()



	# Let's hardcode some values for right now...right
	# MASSIVE DEBUG / TODO / LOOK FOR ME

	args.selected_transport = "transport_imgur"
	args.selected_encoder = "encoder_lsbjpg"
	args.config_path = "sample_builder_config.config.sample"
	args.selected_framework = "cobalt_strike"


	# Let's load our config file
	config = load_config(args.config_path)

	# Create the builder object
	build = builder.Builder()

	# Let's assign the proper builder variables
	build.encoder = str(args.selected_encoder)
	build.transport = str(args.selected_transport)
	build.framework = str(args.selected_framework)
	build.build_path = str(args.build_path)


	# Run any tasks required to prepare the builder before hand.
	build.prep_builder()

	print "Building file(s) for %s, with %s and %s at %s" %(args.selected_framework, args.selected_transport, args.selected_encoder, args.build_path)

	