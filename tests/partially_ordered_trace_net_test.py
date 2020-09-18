import unittest
import pm4py.objects.log
import os
from pm4py.objects.log.importer.xes import factory as importer
from pm4py.objects.petri.petrinet import PetriNet
from pm4py.objects.petri import utils
from pm4py.visualization.petrinet import factory as pn_vis_factory


class TestPartiallyOrderedTraceNet(unittest.TestCase):
    def setUp(self):
        self.trace_net = PetriNet('trace net of %s' % str(1))
        
        activities = ['a', 'b', 'c', 'd']
        transitions = []
        artificial_start_transition = PetriNet.Transition('start', 'start')
        artificial_end_transition = PetriNet.Transition('end', 'end')
        
        place = PetriNet.Place('p_0')
        self.trace_net.places.add(place)
        utils.add_arc_from_to(place, artificial_start_transition, self.trace_net)
        self.trace_net.transitions.add(artificial_start_transition)
        self.trace_net.transitions.add(artificial_end_transition)
        
        i = 0
        for index, activity in enumerate(activities):
            place = PetriNet.Place('p_'+ str(i))
            self.trace_net.places.add(place)
            utils.add_arc_from_to(artificial_start_transition, place , self.trace_net)
            transition = PetriNet.Transition('t_' + activities[index] + '_' + str(index), activities[index] )
            self.trace_net.transitions.add(transition)
            utils.add_arc_from_to(place, transition , self.trace_net)
            place = PetriNet.Place('p_'+ str(i+1))
            self.trace_net.places.add(place)
            utils.add_arc_from_to(transition, place , self.trace_net)
            utils.add_arc_from_to(place, artificial_end_transition, self.trace_net)
            i = i+1
        
        place = PetriNet.Place('p_'+ str(i))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(artificial_end_transition, place, self.trace_net)

        transition_a = [transition for transition in self.trace_net.transitions if transition.label == 'a'][0]
        transition_b = [transition for transition in self.trace_net.transitions if transition.label == 'b'][0]
        transition_c = [transition for transition in self.trace_net.transitions if transition.label == 'c'][0]
        transition_d = [transition for transition in self.trace_net.transitions if transition.label == 'd'][0]

        place = PetriNet.Place('p_'+ str(i+1))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(transition_a, place, self.trace_net)
        utils.add_arc_from_to(place, transition_b, self.trace_net)

        place = PetriNet.Place('p_'+ str(i+2))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(transition_a, place, self.trace_net)
        utils.add_arc_from_to(place, transition_c, self.trace_net)

        place = PetriNet.Place('p_'+ str(i+3))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(transition_a, place, self.trace_net)
        utils.add_arc_from_to(place, transition_d, self.trace_net)

        place = PetriNet.Place('p_'+ str(i+4))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(transition_b, place, self.trace_net)
        utils.add_arc_from_to(place, transition_d, self.trace_net)

        place = PetriNet.Place('p_'+ str(i+5))
        self.trace_net.places.add(place)
        utils.add_arc_from_to(transition_c, place, self.trace_net)
        utils.add_arc_from_to(place, transition_d, self.trace_net)

        filename = "partially_ordered_test_log.xes"
        path = os.path.join("/GitHub/pm4py-source/tests/input_data", filename)
        self.log = importer.import_log(path)

    def test_partially_ordered_trace_net_creation(self):
        partially_ordered_trace_net, initial_marking, final_marking = utils.construct_partially_ordered_trace_net(self.log[0])
        pn_vis_factory.view(pn_vis_factory.apply(partially_ordered_trace_net, parameters={"format": "svg"}))
        self.assertEqual(len(self.trace_net.transitions), len(partially_ordered_trace_net.transitions))
        self.assertEqual(len(self.trace_net.places), len(partially_ordered_trace_net.places))

if __name__ == "__main__":
    unittest.main()


        

