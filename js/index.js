import { FrameToStream, FrameToFrame, createEvent } from "../../../core/client/client.js";
import { segment } from "oicq";

export const rule = {
  tarot: {
    reg: "^#塔罗牌$",
    priority: 800,
    describe: "塔罗牌",
  },
  divine: {
    reg: "^#占卜",
    priority: 800,
    describe: "占卜",
  },
};

export async function tarot(e) {
  FrameToFrame({
    _package: "tarot",
    _handler: "tarot",
    params: {
      event: await createEvent(e),
    },
    onData: (error, response) => {
      if (error) {
        console.log(error.stack);
      } else {
        let msg = [];

        if (response.message) {
          msg.push(response.message);
        }

        if (response.messageDict.at) {
          msg.push(segment.at(response.messageDict.at));
        }

        if (response.image) {
          msg.push(segment.image(response.image));
        }
        e.reply(msg);
      }
    },
  });
  return true;
}

export async function divine(e) {
  let msg = [];
  FrameToStream({
    _package: "tarot",
    _handler: "divine",
    params: {
      event: await createEvent(e),
    },
    onData: (error, response) => {
      if (error) {
        console.log(error.stack);
      } else {
        if (!msg.length) {
          msg.push(segment.at(response.messageDict.at));
        }

        if (response.message) {
          msg.push(response.message);
        }

        if (response.image.length) {
          msg.push(segment.image(response.image));
        }
      }
    },
  }).on("end", () => {
    e.reply(msg);
  });
  return true;
}
