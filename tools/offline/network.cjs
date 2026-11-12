// Verification-only Node guard. Local browser/server sockets and named pipes work.
const net = require("node:net");
const fs = require("node:fs");
const original = net.Socket.prototype.connect;
const local = new Set(["127.0.0.1", "::1", "localhost"]);
net.Socket.prototype.connect = function (...args) {
  let value = args[0];
  if (Array.isArray(value)) value = value[0];
  if (typeof value === "string" && !/^\d+$/.test(value)) {
    return original.apply(this, args); // Named-pipe IPC, not an IP connection.
  }
  const host = typeof value === "object"
    ? value.host || "localhost"
    : typeof args[1] === "string" ? args[1] : "localhost";
  if (!local.has(host)) {
    if (process.env.AUGPHYS_OFFLINE_LOG) {
      fs.appendFileSync(process.env.AUGPHYS_OFFLINE_LOG,
        JSON.stringify({runtime: "node", event: "socket.connect", host}) + "\n");
    }
    throw new Error("M0 verification blocks external network access");
  }
  return original.apply(this, args);
};
