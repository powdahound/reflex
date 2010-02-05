

class RedisReplyParser(basic.LineReceiver):

    bulk_length = 0
    multi_bulk_length = 0
    multi_bulk_reply = []

    ERROR = "-"
    STATUS = "+"
    INTEGER = ":"
    BULK = "$"
    MULTI_BULK = "*"

    def __init__(self):
        self.replyQueue = defer.DeferredQueue()

    def lineReceived(self, line):
        """
        Reply types:
          "-" error message
          "+" single line status reply
          ":" integer number (protocol level only?)

          "$" bulk data
          "*" multi-bulk data
        """
        token = line[0] # first byte indicates reply type
        data = line[1:]
        if token == self.ERROR:
            self.errorReceived(data)
        elif token == self.STATUS:
            self.statusReceived(data)
        elif token == self.INTEGER:
            self.integerReceived(data)
        elif token == self.BULK:
            try:
                self.bulk_length = int(data)
            except ValueError:
                self.replyReceived(InvalidResponse("Cannot convert data '%s' to integer" % data))
                return 
            if self.bulk_length == -1:
                self.bulkDataReceived(None)
            else:
                self.setRawMode()
        elif token == self.MULTI_BULK:
            try:
                self.multi_bulk_length = int(data)
            except (TypeError, ValueError):
                self.replyReceived(InvalidResponse("Cannot convert multi-response header '%s' to integer" % data))
                return
            if self.multi_bulk_length == -1:
                self.multi_bulk_reply = None
                self.multiBulkDataReceived()
            if self.multi_bulk_length == 0:
                self.multiBulkDataReceived()
 

    def rawDataReceived(self, data):
        """
        Process and dispatch to bulkDataReceived.
        """
        bulk_data = data[:self.bulk_length]
        rest_data = data[self.bulk_length:]
        self.bulkDataReceived(bulk_data)
        self.setLineMode(extra=rest_data)

    def errorReceived(self, data):
        """
        Error from server.
        """
        reply = ResponseError(data[4:] if data[:4] == 'ERR ' else data)
        self.replyReceived(reply)

    def statusReceived(self, data):
        """
        Single line status should always be a string.
        """
        if data == 'none':
            reply = None # should this happen here in the client?
        else:
            reply = data 
        self.replyReceived(reply)

    def integerReceived(self, data):
        """
        For handling integer replies.
        """
        try:
            reply = int(data) 
        except ValueError:
            reply = InvalidResponse("Cannot convert data '%s' to integer" % data)
        self.replyReceived(reply)


    def bulkDataReceived(self, data):
        """
        Receipt of a bulk data element.
        """
        self.bulk_length = 0
        element = data #  add types

        try:
            element = int(data) if data.find('.') == -1 else decimal.Decimal(data)
        except (ValueError, decimal.InvalidOperation):
            element = data.decode(self.charset)

        if self.multi_bulk_length > 0:
            self.handleMultiBulkElement(element)
        else:
            self.replyReceived(element)

    def handleMultiBulkElement(self, element):
        self.multi_bulk_reply.append(element)
        self.multi_bulk_length = self.multi_bulk_length - 1
        if self.multi_bulk_length == 0:
            self.multiBulkDataReceived()


    def multiBulkDataReceived(self):
        """
        Receipt of list or set of bulk data elements.
        """
        reply, self.multi_bulk_reply = self.multi_bulk_reply, []
        self.multi_bulk_length = 0
        self.replyReceived(reply)
        

    def replyReceived(self, reply):
        """
        Complete reply received and ready to be pushed to the requesting
        function.
        """
        self.replyQueue.put(reply)





