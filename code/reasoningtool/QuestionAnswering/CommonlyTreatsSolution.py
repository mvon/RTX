# This script will return X that are similar to Y based on high Jaccard index of common one-hop nodes Z (X<->Z<->Y)

import os
import sys
import argparse
# PyCharm doesn't play well with relative imports + python console + terminal
try:
	from code.reasoningtool import ReasoningUtilities as RU
except ImportError:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	import ReasoningUtilities as RU

import FormatOutput
import networkx as nx
try:
	from QueryCOHD import QueryCOHD
except ImportError:
	sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
	try:
		from QueryCOHD import QueryCOHD
	except ImportError:
		sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kg-construction'))
		from QueryCOHD import QueryCOHD

from COHDUtilities import COHDUtilities

import CustomExceptions


class CommonlyTreatsSolution:

	def __init__(self):
		None

	@staticmethod
	def answer(drug_id, use_json=False, num_show=20, rev=True, conservative=True):
		"""
		Answers the question 'what diseases does $drug commonly treat?'
		:param disease_id: KG disease node name
		:param use_json: bool, use JSON output
		:param num_show: int, number to display
		:param rev: bool. order by most frequent
		:param conservative: bool, True if using exact matches, False if using any synonyms returned by COHD
		:return: none
		"""

		# Initialize the response class
		response = FormatOutput.FormatResponse(6)

		# get the description
		drug_description = RU.get_node_property(drug_id, 'name')

		# Get the conditions that COHD says it's used to treat
		conditions_treated = COHDUtilities.get_conditions_treating(drug_description, conservative=conservative)

		# sort the diseases by frequency
		ids_counts = []
		for id in conditions_treated:
			cond = conditions_treated[id]
			ids_counts.append((id, cond['concept_count']))

		ids_counts_sorted = sorted(ids_counts, key=lambda x: x[1], reverse=rev)
		ids_sorted = [i[0] for i in ids_counts_sorted]

		# reduce to top n
		ids_sorted_top_n = ids_sorted
		if len(ids_sorted_top_n) > num_show:
			ids_sorted_top_n = ids_sorted_top_n[0:num_show]

		# return the results
		if not use_json:
			if rev:
				to_print = "The most common conditions  "
			else:
				to_print = "The least common conditions "
			to_print += "treated with %s, according to the Columbia Open Health Data, are:\n" % drug_description
			for id in ids_sorted_top_n:
				to_print += "condition: %s\t count %d \t frequency %f \n" % (conditions_treated[id]['associated_concept_name'], conditions_treated[id]['concept_count'], conditions_treated[id]['concept_frequency'])
			print(to_print)
		else:
			for id in ids_sorted_top_n:
				disease_name = conditions_treated[id]['associated_concept_name']
				disease_count = conditions_treated[id]['concept_count']
				disease_frequency = conditions_treated[id]['concept_frequency']
				in_graph = False
				if RU.node_exists_with_property(disease_name, 'name'):
					disease_as_graph = RU.get_node_as_graph(disease_name, use_description=True)
					disease_properties = list(nx.get_node_attributes(disease_as_graph, 'properties').values())[0]
					disease_id = disease_properties['rtx_name']
					in_graph = True
				elif RU.node_exists_with_property(disease_name.lower(), 'name'):
					disease_as_graph = RU.get_node_as_graph(disease_name.lower(), use_description=True)
					disease_properties = list(nx.get_node_attributes(disease_as_graph, 'properties').values())[0]
					disease_id = disease_properties['rtx_name']
					in_graph = True

				if in_graph:
					to_print = "According to the Columbia Open Health Data, %s treats the condition %s with frequency " \
							   "%f out of all patients treated with %s (count=%d)." % (
					drug_description, disease_name, disease_frequency, drug_description, disease_count)
					drug_as_graph = RU.get_node_as_graph(drug_id)
					nodes = []
					disease_node_info = disease_as_graph.nodes(data=True)[0][1]
					drug_node_info = drug_as_graph.nodes(data=True)[0][1]
					nodes.append((2, disease_node_info))
					nodes.append((1, drug_node_info))
					edges = [(1, 2, {'id': 3, 'properties': {'is_defined_by': 'RTX',
							'predicate': 'treats',
							'provided_by': 'COHD',
							'relation': 'treats',
							'seed_node_uuid': '-1',
							'source_node_uuid': drug_node_info['properties']['UUID'],
							'target_node_uuid': disease_node_info['properties']['UUID']},
							'type': 'treats'})]
					response.add_subgraph(nodes, edges, to_print, disease_frequency)
				else:
					to_print = "According to the Columbia Open Health Data, %s treats the condition %s with frequency " \
							   "%f out of all patients treated with %s (count=%d). This condition is not in our " \
							   "Knowledge graph, so no graph is shown." % (
								   drug_description, disease_name, disease_frequency, drug_description, disease_count)
					g = RU.get_node_as_graph(drug_id)
					response.add_subgraph(g.nodes(data=True), g.edges(data=True), to_print, disease_frequency)
			response.print()

	@staticmethod
	def describe():
		output = "Answers questions of the form: 'What conditions does $drug treat?'" + "\n"
		# TODO: subsample disease nodes
		return output


def main():
	parser = argparse.ArgumentParser(description="Answers questions of the form: 'What conditions does $drug treat?'",
									formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('-d', '--drug', type=str, help="drug ID/name", default="CHEMBL154")
	parser.add_argument('-r', '--rare', action='store_true', help="Include if you want the least common diseases, don't include if you want the most common")
	parser.add_argument('-c', '--conservative', action='store_true', help="Include if you want exact matches to drug name (so excluding combo drugs)")
	parser.add_argument('-j', '--json', action='store_true', help='Flag specifying that results should be printed in JSON format (to stdout)', default=False)
	parser.add_argument('--describe', action='store_true', help='Print a description of the question to stdout and quit', default=False)
	parser.add_argument('--num_show', type=int, help='Maximum number of results to return', default=50)

	# Parse and check args
	args = parser.parse_args()
	drug_id = args.drug
	is_rare = args.rare
	is_conservative = args.conservative
	use_json = args.json
	describe_flag = args.describe
	num_show = args.num_show


	# Initialize the question class
	Q = CommonlyTreatsSolution()

	if describe_flag:
		res = Q.describe()
		print(res)
	else:
		Q.answer(drug_id, use_json=use_json, num_show=num_show, rev=not(is_rare), conservative=is_conservative)


if __name__ == "__main__":
	main()
