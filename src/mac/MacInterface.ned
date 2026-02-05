package lifihiddennode.mac;

moduleinterface MacInterface
{
    parameters:
        int numNodes = 4;
        int numHops = 1;
    gates:
        input in;
        output out;
}
