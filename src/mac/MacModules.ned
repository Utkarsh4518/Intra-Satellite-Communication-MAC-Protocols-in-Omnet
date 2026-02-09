package lifihiddennode.mac;

import lifihiddennode.mac.MacInterface;

simple MacTDMA like MacInterface
{
    gates:
        input in;
        output out;
}

simple MacCSMA like MacInterface
{
    parameters:
        int maxRetries = 4;
        double initialBackoff = 0.01;
        double maxBackoff = 0.5;
        volatile double deferMax = 0.03;   // Max random defer before first transmission attempt (s)
        volatile double hopDelayMax = 0.02;  // Max delay before next-hop transmission, multi-hop (s)
    gates:
        input in;
        output out;
}

simple MacCSMA_RTS like MacInterface
{
    parameters:
        volatile double rtsHopDelay = 0.01;  // Delay between RTS hops, multi-hop (s)
    gates:
        input in;
        output out;
}

simple MacALOHA like MacInterface
{
    parameters:
        volatile double retxMean = 0.05;     // Mean time before retransmission after collision, exponential (s)
        volatile double hopDelayMax = 0.02;  // Max delay before next-hop transmission, multi-hop (s)
    gates:
        input in;
        output out;
}
