import urllib.request
import json
import time
import debug
import threading


class ApiManager:
    """Management functionality for API calls.

    Attributes:
        lastcall (int): Timestamp (in ms) of last API call
    """
    API_LIMIT_PER_SECOND = 100  # 100
    API_LIMIT_PER_HOUR = 36000

    def __init__(self):
        # Instance method
        self.lastcall = self.gettime()
        self.callspersecond = self.calculaterate("second")
        self.callsperhour = self.calculaterate("hour")
        self.callsmade = []
        self.inputqueue = []
        self.outputqueue = []
        self.started = False
        self.finished = False
        self.failedcalls = []

    def initiatecall(self):
        """Begin calling on API.
        """
        if len(self.inputqueue) > 0:
            while self.cancall() is False:
                self.nap()

            thread = threading.Thread(target=self.initiatecall)
            thread.start()
            self.started = True

            success, item, reason = self.apicall(asjson=True)

            if item is not None:
                data, queuetype = item

            if success:
                self.outputqueue.append((data, queuetype))
            else:
                # TODO: Figure out why calls fail in the first place?
                # Rate limit exceeded...probably?
                if reason == "API_CALL_FAIL":
                    self.addqueue((data, queuetype))

    def getactivethreads(self):
        """Returns number of active threads.

        Returns:
            int: Active thread count
        """
        return threading.active_count()

    def returnoutputqueue(self, getqueuetype):
        """Returns current output queue.

        Returns:
            list: Output queue

        Args:
            getqueuetype (str): Type of API call
        """
        returnqueue = []
        for data, queuetype in self.outputqueue:
            if queuetype == getqueuetype:
                returnqueue.append(data)

        return returnqueue

    def isinputqueueempty(self):
        """Returns True if input queue is empty otherwise False

        Returns:
            bool: True if input queue is empty otherwise False
        """
        if len(self.inputqueue) == 0:
            return True
        else:
            return False

    def nap(self):
        """Go to sleep for 1 iteration of smaller API limit
        """
        time.sleep(self.callspersecond / 1000)

    def loadqueue(self, data):
        """Bulk insert (extend) input queue.

        Args:
            data (list): List of items to add to end of queue
        """
        self.inputqueue.extend(data)

    def addqueue(self, url, queuetype):
        """Add a URL to end of queue list (FIFO).

        Args:
            url (str): API call URL
            queuetype (str): Type of API call
        """
        self.inputqueue.append((url, queuetype))

    def getnextitem(self):
        """Returns next item queued (FIFO).

        Returns:
            str: API call URL
        """
        if len(self.inputqueue) > 0:
            return self.inputqueue.pop(0)
        else:
            return None

    def gettime(self):
        """Returns current time in milliseconds.

        Returns:
            int: Current time in milliseconds
        """
        return int(round(time.time() * 1000))

    def logcall(self):
        """Log the time of API call.
        """
        self.callsmade.append(self.gettime())

    def calculaterate(self, timeframe):
        """Return a rate limit based on timeframe and defined API_LIMIT_PER_<timeframe>.

        Args:
            timeframe (str): Timeframe based on limitations imposed on API calls

        Returns:
            int: Milliseconds to wait between API calls
        """
        if timeframe == "second":
            return (1 / self.API_LIMIT_PER_SECOND) * 1000
        elif timeframe == "hour":
            return (1 / (self.API_LIMIT_PER_HOUR / 60 / 60)) * 1000
        else:
            return (1 * 1000)   # Default rate of 1 call per second

    def jsonload(self, data, queuetype):
        """Convert (JSON formatted) string to JSON dictionary.

        Args:
            data (str): JSON string to load
            queuetype (str): Type of API call

        Returns:
            tuple(bool, dict): True with JSON dictionary on successful load or False with original data
        """
        try:
            return (True, (json.loads(data), queuetype), "SUCCESS")
        except Exception as e:
            debug.log("JSON load failed for: {data}".format(data=data), traceback=False)
            return (False, (data, queuetype), "JSON_FAIL")

    def timediff(self):
        """Time in milliseconds since last API call.

        Returns:
            int: Milliseconds since last API call
        """
        return self.gettime() - self.lastcall

    def cancall(self):
        """Returns True if you have not exceeded the define API rate limits.

        Returns:
            bool: True if call will not exceed rate limit otherwise False
        """
        callsinlastsecond = [call for call in self.callsmade if call >= self.gettime() - 1000]
        if len(callsinlastsecond) >= self.API_LIMIT_PER_SECOND:
            debug.debug("Rejecting due to rate limit...", output=False, flush=True)
            return False

        callsinlasthour = [call for call in self.callsmade if call >= self.gettime() - (1000 * 60 * 60)]
        if len(callsinlasthour) >= self.API_LIMIT_PER_HOUR:
            debug.debug("Rejecting due to hourly limit...", output=False, flush=True)
            return False

        if threading.active_count() >= self.API_LIMIT_PER_SECOND - 5:   # Help prevent collisions
            debug.debug("Rejecting due to thread count...", output=False, flush=True)
            return False

        return True

    def apicall(self, asjson=True):
        """Requests data from URL via API call.

        If asjson is True and JSON loaded, returns True with JSON dictionary.

        If asjson is True and JSON didn't load, returns False with data returned from API call.

        If asjson is False, returns True and data returned from API call or False and the URL passed.

        Args:
            asjson (bool, optional): Return data as JSON dictionary

        Returns:
            tuple(bool, str): True with data if success

        """
        # TODO: Implement Threading event when call can be made?
        try:
            item = self.getnextitem()
            data = ""
            if item is not None:
                # print(url)
                self.logcall()
                url, queuetype = item
                with urllib.request.urlopen(url) as url:
                    data = url.read().decode()

                if asjson:
                    return self.jsonload(data, queuetype)
                else:
                    return (True, (data, queuetype), "SUCCESS")
            else:
                return (False, None, "URL_MISSING")
        except Exception as e:
            debug.log("{e}\nAPI call failed for URL: {url}".format(e=str(e), url=url), traceback=False)
            return (False, item, "API_CALL_FAIL")
