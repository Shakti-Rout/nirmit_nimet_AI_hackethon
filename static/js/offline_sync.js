// ==========================================================================
// Prerana AI - Offline Sync & Resilience Manager
// Directly implements Hackathon Bonus Criteria for Offline Compatibility
// ==========================================================================

class OfflineManager {
  constructor() {
    this.isOffline = false;
    this.storageKey = "prerana_offline_queue";
    this.cachedCurriculumKey = "prerana_cached_curriculum";
    this.initPreloadCache();
  }

  setOffline(status) {
    this.isOffline = status;
    const banner = document.getElementById("offlineBanner");
    const netBadge = document.getElementById("networkBadge");
    const netText = document.getElementById("networkText");
    const netDot = document.getElementById("networkDot");

    if (banner && netBadge && netText && netDot) {
      if (this.isOffline) {
        banner.style.display = "flex";
        netBadge.className = "network-badge offline";
        netText.textContent = "Offline Mode (Simulated)";
        netDot.className = "status-dot red";
      } else {
        banner.style.display = "none";
        netBadge.className = "network-badge online";
        netText.textContent = "Online Mode";
        netDot.className = "status-dot green";
      }
    }

    this.updateSyncBadge();
  }

  toggleOffline() {
    this.setOffline(!this.isOffline);
  }

  initPreloadCache() {
    // Pre-cache core lesson vectors in localStorage for client-side zero-connection fallback
    const offlineCurriculum = {
      "newton": {
        topic: "Newton's Laws of Motion",
        or: "ନିଉଟନଙ୍କ ତୃତୀୟ ଗତି ନିୟମ: ପ୍ରତ୍ୟେକ କ୍ରିୟାର ସମାନ ଏବଂ ବିପରୀତ ପ୍ରତିକ୍ରିୟା ଥାଏ। ଉଭୟ ବଳ ଭିନ୍ନ ବସ୍ତୁ ଉପରେ କାର୍ଯ୍ୟ କରନ୍ତି।",
        en: "Newton's Third Law states that every action has an equal and opposite reaction acting on two different bodies."
      },
      "photosynthesis": {
        topic: "Photosynthesis",
        or: "ଆଲୋକ ଶ୍ଳେଷଣ: ସବୁଜ ଉଦ୍ଭିଦ ସୂର୍ଯ୍ୟାଲୋକ ଓ ହରିତ୍‌କଣା ସାହାଯ୍ୟରେ ଜଳ ଓ ଅଙ୍ଗାରକାମ୍ଳରୁ ଗ୍ଲୁକୋଜ ଓ ଅମ୍ଳଜାନ ପ୍ରସ୍ତୁତ କରେ।",
        en: "Photosynthesis converts CO2 and H2O into glucose and O2 in the presence of sunlight and chlorophyll."
      }
    };
    if (!localStorage.getItem(this.cachedCurriculumKey)) {
      localStorage.setItem(this.cachedCurriculumKey, JSON.stringify(offlineCurriculum));
    }
  }

  queueOfflineEvent(eventType, topic, delta = 10, metadata = {}) {
    const queue = this.getQueue();
    const eventItem = {
      id: "ev_" + Date.now() + "_" + Math.random().toString(36).substr(2, 5),
      type: eventType,
      topic: topic,
      mastery_delta: delta,
      metadata: metadata,
      timestamp: new Date().toISOString()
    };
    queue.push(eventItem);
    localStorage.setItem(this.storageKey, JSON.stringify(queue));
    this.updateSyncBadge();
    return eventItem;
  }

  getQueue() {
    try {
      const q = localStorage.getItem(this.storageKey);
      return q ? JSON.parse(q) : [];
    } catch (e) {
      return [];
    }
  }

  clearQueue() {
    localStorage.removeItem(this.storageKey);
    this.updateSyncBadge();
  }

  updateSyncBadge() {
    const queue = this.getQueue();
    const syncBtn = document.getElementById("syncNowBtn");
    const queueCounter = document.getElementById("devQueueCount");

    if (syncBtn) {
      if (queue.length > 0) {
        syncBtn.style.display = "inline-flex";
        syncBtn.textContent = `Sync Offline Data (${queue.length})`;
      } else {
        syncBtn.style.display = "none";
      }
    }

    if (queueCounter) {
      queueCounter.textContent = queue.length;
    }
  }

  async syncBatch(userEmail = "student@prerana.ai") {
    const queue = this.getQueue();
    if (queue.length === 0) {
      alert("No pending offline events to synchronize.");
      return;
    }

    try {
      const resp = await fetch("/api/sync/offline-batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          offline_events: queue,
          user_email: userEmail
        })
      });
      const data = await resp.json();

      if (data.status === "success") {
        this.clearQueue();
        alert(`Offline Sync Complete! ${data.synced_count} events reconciled. Mastery updated.`);
        if (window.app && window.app.refreshStudentMastery) {
          window.app.refreshStudentMastery(data.updated_mastery);
        }
      }
    } catch (err) {
      alert("Sync failed: Central server is unreachable. Events remain queued safely.");
    }
  }
}

window.offlineManager = new OfflineManager();
