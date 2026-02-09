#include <omnetpp.h>
#include "MacBase.cc"

using namespace omnetpp;

class MacALOHA : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    cMessage *burstEvent = nullptr;
    simtime_t currentPacketGenTime;
    int hopsCompleted = 0;

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
            txAttempts++;
            currentPacketGenTime = simTime();
            hopsCompleted = 0;
            send(new cMessage("data", 1), "out");
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

        if (strcmp(msg->getName(), "reTX") == 0 || strcmp(msg->getName(), "hop") == 0) {
            txAttempts++;
            send(new cMessage("data", 1), "out");
            delete msg;
            return;
        }

        send(new cMessage("end", 0), "out");

        if (msg->getKind() == 99) {
            collisions++;
            double retxMean = par("retxMean").doubleValue();
            scheduleAt(simTime() + exponential(retxMean), new cMessage("reTX"));
        } else {
            int numHops = (int)par("numHops");
            hopsCompleted++;
            double hopDly = par("hopDelayMax").doubleValue();
            if (hopsCompleted >= numHops) {
                recordDelivery(currentPacketGenTime);
                scheduleNextGen();
            } else {
                scheduleAt(simTime() + uniform(0, hopDly), new cMessage("hop"));
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

Define_Module(MacALOHA);
