#include <omnetpp.h>
#include "MacBase.cc"
#include <cmath>

using namespace omnetpp;

class MacCSMA : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    cMessage *burstEvent = nullptr;
    int retryCount = 0;
    int hopsCompleted = 0;
    simtime_t currentPacketGenTime;

    void scheduleNextGen() {
        const char *profile = par("trafficProfile").stringValue();
        if (strcmp(profile, "periodicWithBurst") == 0) {
            double base = par("baseInterval").doubleValue();
            genEvent = new cMessage("gen");
            scheduleAt(simTime() + base, genEvent);
        } else {
            double pktInt = par("packetInterval").doubleValue();
            genEvent = new cMessage("gen");
            scheduleAt(simTime() + pktInt, genEvent);
        }
    }

  protected:
    void initialize() override {
        const char *profile = par("trafficProfile").stringValue();
        genEvent = new cMessage("gen");
        if (strcmp(profile, "periodicWithBurst") == 0) {
            double base = par("baseInterval").doubleValue();
            double burstInt = par("burstInterval").doubleValue();
            scheduleAt(simTime() + uniform(0, base), genEvent);
            burstEvent = new cMessage("burst");
            scheduleAt(simTime() + burstInt, burstEvent);
        } else {
            double pktInt = par("packetInterval").doubleValue();
            scheduleAt(simTime() + uniform(0, pktInt), genEvent);
        }
    }

    void handleMessage(cMessage *msg) override {
        if (msg == genEvent || strcmp(msg->getName(), "burstPkt") == 0) {
            generated++;
            retryCount = 0;
            hopsCompleted = 0;
            currentPacketGenTime = simTime();
            double deferMax = par("deferMax").doubleValue();
            simtime_t defer = uniform(0, deferMax);
            scheduleAt(simTime() + defer, new cMessage("tx"));
            if (msg == genEvent) {
                genEvent = nullptr;
                cancelAndDelete(msg);
                scheduleNextGen();
            } else
                delete msg;
            return;
        }

        if (msg == burstEvent) {
            double burstInt = par("burstInterval").doubleValue();
            int n = (int)par("burstSize");
            double ipb = par("interPacketInBurst").doubleValue();
            for (int k = 0; k < n; k++)
                scheduleAt(simTime() + k * ipb, new cMessage("burstPkt"));
            burstEvent = new cMessage("burst");
            scheduleAt(simTime() + burstInt, burstEvent);
            delete msg;
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
                scheduleNextGen();
            }
        } else {
            int numHops = (int)par("numHops");
            hopsCompleted++;
            double hopDly = par("hopDelayMax").doubleValue();
            if (hopsCompleted >= numHops) {
                recordDelivery(currentPacketGenTime);
                scheduleNextGen();
            } else {
                scheduleAt(simTime() + uniform(0, hopDly), new cMessage("tx"));
            }
        }

        delete msg;
    }

    void finish() override {
        if (genEvent) cancelAndDelete(genEvent);
        if (burstEvent) cancelAndDelete(burstEvent);
        MacBase::finish();
    }
};

Define_Module(MacCSMA);
