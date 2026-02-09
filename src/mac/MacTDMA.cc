#include <omnetpp.h>
#include "MacBase.cc"

using namespace omnetpp;

class MacTDMA : public MacBase {
  private:
    simtime_t slotTime;
    cMessage *txEvent = nullptr;
    simtime_t sentTime;
    int hopsLeftForCurrentPacket = 0;
    simtime_t currentPacketGenTime;

  protected:
    void initialize() override {
        int N = (int)par("numNodes");
        double pktInt = par("packetInterval").doubleValue();
        slotTime = pktInt / N;
        int index = getParentModule()->getIndex();
        txEvent = new cMessage("tdma_tx");
        scheduleAt(simTime() + index * slotTime, txEvent);
    }

    void handleMessage(cMessage *msg) override {
        if (msg == txEvent) {
            int numHops = (int)par("numHops");
            if (hopsLeftForCurrentPacket == 0) {
                generated++;
                currentPacketGenTime = simTime();
                hopsLeftForCurrentPacket = numHops;
            }
            txAttempts++;
            sentTime = simTime();
            send(new cMessage("data", 1), "out");
            int N = (int)par("numNodes");
            scheduleAt(simTime() + N * slotTime, txEvent);
        }
        else {
            hopsLeftForCurrentPacket--;
            if (hopsLeftForCurrentPacket == 0)
                recordDelivery(currentPacketGenTime);
            send(new cMessage("end", 0), "out");
            delete msg;
        }
    }

    void finish() override {
        cancelAndDelete(txEvent);
        MacBase::finish();
    }
};

Define_Module(MacTDMA);
