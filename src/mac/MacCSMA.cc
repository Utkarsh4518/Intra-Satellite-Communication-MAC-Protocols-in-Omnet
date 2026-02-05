#include <omnetpp.h>
#include "MacBase.cc"
#include <cmath>

using namespace omnetpp;

class MacCSMA : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    int retryCount = 0;
    int hopsCompleted = 0;
    simtime_t currentPacketGenTime;

  protected:
    void initialize() override {
        genEvent = new cMessage("gen");
        scheduleAt(simTime() + uniform(0, 0.05), genEvent);
    }

    void handleMessage(cMessage *msg) override {
        if (msg == genEvent) {
            generated++;
            retryCount = 0;
            hopsCompleted = 0;
            currentPacketGenTime = simTime();
            simtime_t defer = uniform(0, 0.03);
            scheduleAt(simTime() + defer, new cMessage("tx"));
            cancelAndDelete(genEvent);
            genEvent = nullptr;
            return;
        }

        if (strcmp(msg->getName(), "tx") == 0) {
            txAttempts++;
            send(new cMessage("data", 1), "out");
            delete msg;
            return;
        }

        int kind = msg->getKind();
        send(new cMessage("end", 0), "out");

        if (kind == 99) {
            collisions++;
            retryCount++;
            int maxRetries = (int)par("maxRetries");
            double initialBackoff = par("initialBackoff").doubleValue();
            double maxBackoff = par("maxBackoff").doubleValue();

            if (retryCount <= maxRetries) {
                double backoff = initialBackoff * pow(2.0, (double)(retryCount - 1));
                if (backoff > maxBackoff) backoff = maxBackoff;
                scheduleAt(simTime() + backoff, new cMessage("tx"));
            } else {
                retriesExhausted++;
                genEvent = new cMessage("gen");
                scheduleAt(simTime() + 0.05, genEvent);
            }
        } else {
            int numHops = (int)par("numHops");
            hopsCompleted++;
            if (hopsCompleted >= numHops) {
                recordDelivery(currentPacketGenTime);
                genEvent = new cMessage("gen");
                scheduleAt(simTime() + 0.05, genEvent);
            } else {
                scheduleAt(simTime() + uniform(0, 0.02), new cMessage("tx"));
            }
        }

        delete msg;
    }

    void finish() override {
        if (genEvent) cancelAndDelete(genEvent);
        MacBase::finish();
    }
};

Define_Module(MacCSMA);
