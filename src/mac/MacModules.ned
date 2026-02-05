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
    gates:
        input in;
        output out;
}

simple MacCSMA_RTS like MacInterface
{
    gates:
        input in;
        output out;
}

simple MacALOHA like MacInterface
{
    gates:
        input in;
        output out;
}
