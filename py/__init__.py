from .data_source import Tarot
from core import Handler, Request, Response, ResponseIterator

package = "tarot"


@Handler.FrameToFrame
async def tarot(request: Request) -> Response:
    return Response(**await Tarot.tarot(), messageDict={"at": request.event.sender.qq})


@Handler.FrameToStream
async def divine(request: Request) -> ResponseIterator:
    async for res in Tarot.divine():
        yield Response(**res, messageDict={"at": request.event.sender.qq})
