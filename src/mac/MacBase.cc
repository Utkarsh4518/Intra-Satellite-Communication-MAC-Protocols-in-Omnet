#include <omnetpp.h>
#include <cmath>
using namespace omnetpp;

class MacBase : public cSimpleModule {
  protected:
    int generated = 0;
    int txAttempts = 0;
    int collisions = 0;
    int delivered = 0;
    int retriesExhausted = 0;
    double sumDelay = 0;
    double sumDelaySq = 0;
    simtime_t maxDelay = 0;

    virtual void initialize() override {}
    virtual void handleMessage(cMessage *msg) override {}

    void recordDelivery(simtime_t genTime) {
        delivered++;
        simtime_t d = simTime() - genTime;
        double dx = d.dbl();
        sumDelay += dx;
        sumDelaySq += dx * dx;
        if (d > maxDelay) maxDelay = d;
    }

    virtual void finish() override {
        recordScalar("Generated", generated);
        recordScalar("TX_Attempts", txAttempts);
        recordScalar("Collisions", collisions);
        recordScalar("Delivered", delivered);
        recordScalar("RetriesExhausted", retriesExhausted);
        recordScalar("PDR",
            generated > 0 ? (double)delivered / generated : 0.0);
        if (delivered > 0)
            recordScalar("AvgTxAttemptsPerDelivery", (double)txAttempts / delivered);
        if (delivered > 0) {
            double mean = sumDelay / delivered;
            double variance = (sumDelaySq / delivered) - (mean * mean);
            if (variance < 0) variance = 0;
            recordScalar("E2EDelayMean", mean);
            recordScalar("E2EDelayMax", maxDelay.dbl());
            recordScalar("E2EDelayJitter", std::sqrt(variance));
        }
    }
};
