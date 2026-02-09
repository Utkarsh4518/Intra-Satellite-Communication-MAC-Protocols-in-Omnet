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
    int deadlineMisses = 0;
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
        if (hasPar("deadline") && dx > par("deadline").doubleValue())
            deadlineMisses++;
    }

    virtual void finish() override {
        recordScalar("Generated", generated);
        recordScalar("TX_Attempts", txAttempts);
        recordScalar("Delivered", delivered);

        recordScalar("Collisions", collisions);
        recordScalar("RetriesExhausted", retriesExhausted);
        recordScalar("PDR", generated > 0 ? (double)delivered / generated : 0.0);

        if (delivered > 0) {
            double mean = sumDelay / delivered;
            double variance = (sumDelaySq / delivered) - (mean * mean);
            if (variance < 0) variance = 0;
            recordScalar("E2EDelayMean", mean);
            recordScalar("E2EDelayMax", maxDelay.dbl());
            recordScalar("E2EDelayJitter", std::sqrt(variance));
        }

        recordScalar("DeadlineMisses", deadlineMisses);
        if (delivered > 0)
            recordScalar("DeadlineMissRatio", (double)deadlineMisses / delivered);
        if (delivered > 0)
            recordScalar("AvgTxAttemptsPerDelivery", (double)txAttempts / delivered);

        if (hasPar("pdrFailureThreshold") && hasPar("deadlineMissRateFailureThreshold") && hasPar("retryExhaustionRateFailureThreshold"))
            logFailureConditions();
    }

    void logFailureConditions() {
        double pdrTh = par("pdrFailureThreshold").doubleValue();
        double dmTh = par("deadlineMissRateFailureThreshold").doubleValue();
        double reTh = par("retryExhaustionRateFailureThreshold").doubleValue();

        double pdr = (generated > 0) ? ((double)delivered / generated) : 0.0;
        double deadlineMissRate = (delivered > 0) ? ((double)deadlineMisses / delivered) : 0.0;
        double retryExhaustionRate = (generated > 0) ? ((double)retriesExhausted / generated) : 0.0;

        int pdrFail = (generated > 0 && pdr < pdrTh) ? 1 : 0;
        int deadlineFail = (delivered > 0 && deadlineMissRate > dmTh) ? 1 : 0;
        int retryFail = (generated > 0 && retryExhaustionRate > reTh) ? 1 : 0;

        recordScalar("PDRFailure", pdrFail);
        recordScalar("DeadlineMissRateFailure", deadlineFail);
        recordScalar("RetryExhaustionRateFailure", retryFail);
        recordScalar("AnyFailure", (pdrFail || deadlineFail || retryFail) ? 1 : 0);

        if (pdrFail)
            EV_WARN << "[Failure detection - assumption] PDR below threshold: module=" << getFullPath() << " PDR=" << pdr << " threshold=" << pdrTh << "\n";
        if (deadlineFail)
            EV_WARN << "[Failure detection - assumption] Deadline miss rate above threshold: module=" << getFullPath() << " rate=" << deadlineMissRate << " threshold=" << dmTh << "\n";
        if (retryFail)
            EV_WARN << "[Failure detection - assumption] Retry exhaustion rate above threshold: module=" << getFullPath() << " rate=" << retryExhaustionRate << " threshold=" << reTh << "\n";
    }
};
