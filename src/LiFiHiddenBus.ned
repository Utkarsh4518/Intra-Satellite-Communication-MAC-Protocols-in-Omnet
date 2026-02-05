package lifihiddennode;

network LiFiHiddenBus
{
    parameters:
        int numNodes = 4;
        int numHops = 1;
    submodules:
        optChan: OpticalChannel;
        node[numNodes]: Node {
            numNodes = numNodes;
            numHops = numHops;
        }
    connections allowunconnected:
        for i=0..numNodes-1 {
            node[i].out --> optChan.in++;
            optChan.out++ --> node[i].in;
        }
}
