package lifihiddennode.mac;

moduleinterface MacInterface
{
    parameters:
        int numNodes = 4;
        int numHops = 1;
        volatile double packetInterval = 0.05;  // Offered load (periodic profile): mean time between packet generations per node (s)
        string trafficProfile = "periodic";     // Traffic profile: "periodic" (low-rate steady) or "periodicWithBurst" (steady + occasional burst)
        volatile double baseInterval = 0.05;    // (periodicWithBurst) Interval between periodic packets (s)
        volatile double burstInterval = 1.0;   // (periodicWithBurst) Time between start of successive bursts (s)
        int burstSize = 5;                      // (periodicWithBurst) Number of packets per burst
        volatile double interPacketInBurst = 0.01;  // (periodicWithBurst) Time between packets within a burst (s)
        volatile double deadline = 1.0;  // Assumption: hypothetical max acceptable delay (s) for observation only; not used for scheduling or discarding
        volatile double pdrFailureThreshold = 0.9;  // Assumption: if PDR < this, failure is logged (observation only; not enforced)
        volatile double deadlineMissRateFailureThreshold = 0.1;  // Assumption: if DeadlineMissRatio > this, failure is logged (observation only; not enforced)
        volatile double retryExhaustionRateFailureThreshold = 0.1;  // Assumption: if (RetriesExhausted/Generated) > this, failure is logged (observation only; not enforced)
    gates:
        input in;
        output out;
}
