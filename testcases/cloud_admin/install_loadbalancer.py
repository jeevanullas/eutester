#!/usr/bin/python

from eucaops import Eucaops
from eutester.eutestcase import EutesterTestCase
from eutester.machine import Machine


class ConfigureLoadBalancer(EutesterTestCase):
    def __init__(self):
        self.setuptestcase()
        self.setup_parser()
        self.parser.add_argument("--img-repo")
        self.get_args()
        # Setup basic eutester object
        self.tester = Eucaops( config_file=self.args.config,password=self.args.password)

    def clean_method(self):
        pass

    def ConfigureELB(self):
        """
        This is where the test description goes
        """
        clcs = self.tester.get_component_machines("clc")
        if len(clcs) == 0:
            raise Exception("Unable to find a CLC")
        first_clc = clcs[0]
        assert isinstance(first_clc,Machine)
        first_clc.add_repo(url=self.args.img_repo, "EucaLoadBalancer")
        first_clc.install("eucalyptus-load-balancer-image-devel")

        load_balancer_bucket = "loadbalancer_vm"
        first_clc.sys("eustore-install-image -t /usr/share/eucalyptus-load-balancer-image-devel/eucalyptus-load-balancer-image-devel.tgz"
                      "-a x86_64 -s loadbalancer -b " + load_balancer_bucket , code=0)
        load_balancer_emi = self.tester.get_emi(location=load_balancer_bucket)
        self.tester.modify_property("loadbalancing.loadbalancer_emi",load_balancer_emi.id)
        self.tester.modify_property("loadbalancing.loadbalancer_instance_type", "m1.small")

if __name__ == "__main__":
    testcase = ConfigureLoadBalancer()
    ### Use the list of tests passed from config/command line to determine what subset of tests to run
    ### or use a predefined list
    list = testcase.args.tests or ["ConfigureELB"]

    ### Convert test suite methods to EutesterUnitTest objects
    unit_list = [ ]
    for test in list:
        unit_list.append( testcase.create_testunit_by_name(test) )

    ### Run the EutesterUnitTest objects
    result = testcase.run_test_case_list(unit_list,clean_on_exit=True)
    exit(result)