package lifihiddennode;

import lifihiddennode.mac.MacInterface;

module Node
{
    parameters:
        string macType;
        int numNodes = 4;
        int numHops = 1;
    gates:
        input in;
        output out;
    submodules:
        mac: <macType> like MacInterface {
            numNodes = numNodes;
            numHops = numHops;
        }
    connections:
        in --> mac.in;
        mac.out --> out;
}
