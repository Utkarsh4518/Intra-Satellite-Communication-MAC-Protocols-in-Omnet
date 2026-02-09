#include <omnetpp.h>
#include "MacBase.cc"

using namespace omnetpp;

class MacCSMA_RTS : public MacBase {
  private:
    cMessage *genEvent = nullptr;
    cMessage *burstEvent = nullptr;
    simtime_t currentPacketGenTime;
    int hopsLeft = 0;

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
            currentPacketGenTime = simTime();
            hopsLeft = (int)par("numHops");
            txAttempts++;
            send(new cMessage("RTS", 10), "out");
            double rtsHop = par("rtsHopDelay").doubleValue();
            scheduleAt(simTime() + rtsHop, new cMessage("rts_hop"));
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

        if (strcmp(msg->getName(), "rts_hop") == 0) {
            hopsLeft--;
            double rtsHop = par("rtsHopDelay").doubleValue();
            if (hopsLeft > 0) {
                txAttempts++;
                send(new cMessage("RTS", 10), "out");
                scheduleAt(simTime() + rtsHop, new cMessage("rts_hop"));
            } else {
                recordDelivery(currentPacketGenTime);
                scheduleNextGen();
            }
            delete msg;
            return;
        }

        if (msg->getKind() == 99) collisions++;
        delete msg;
    }

    void finish() override {
        if (genEvent) cancelAndDelete(genEvent);
        if (burstEvent) cancelAndDelete(burstEvent);
        MacBase::finish();
    }
};

Define_Module(MacCSMA_RTS);
