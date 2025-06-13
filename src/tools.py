import sys
from datetime import datetime, timedelta, timezone

from phi.tools import Toolkit

from utils.logger import CustomException, logging


class CalendarToolkit(Toolkit):
    def __init__(self, service):
        super().__init__(name="calendar_tools")
        self.service = service
        self.ist = timezone(timedelta(hours=5, minutes=30))

        self.register(self.get_current_date_time)
        self.register(self.create_calendar_event)
        self.register(self.search_calendar_event)
        self.register(self.delete_calendar_event)
        self.register(self.list_calendar_event)

    def get_current_date_time(self)->str:
        return datetime.now(self.ist).isoformat()

    def create_calendar_event(
        self,
        title: str,
        start_time: str,
        end_time: str = None,
        description: str = None,
        location: str = None,
        calendarID: str = "primary",
    ) -> str:
        try:
            try:
                start_datetime = datetime.fromisoformat(start_time)
                if start_datetime.tzinfo is None:
                    start_datetime = start_datetime.replace(tzinfo=self.ist)
                logging.info("Start time is in Indian Standard Time")
            except Exception as e:
                logging.info("Error at converting start time")
                raise CustomException(e, sys)

            if end_time is None:
                end_datetime = start_datetime + timedelta(hours=1)
            else:
                try:
                    end_datetime = datetime.fromisoformat(end_time)
                    if end_datetime.tzinfo is None:
                        end_datetime = end_datetime.replace(tzinfo=self.ist)
                    logging.info("End time is in Indian Standard Time")
                except Exception as e:
                    logging.info("Error at converting end time")
                    raise CustomException(e, sys)

            event = {
                "summary": title,
                "location": location,
                "description": description,
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": "Asia/Kolkata",
                },
            }
            event_result = (
                self.service.events()
                .insert(calendarId=calendarID, body=event)
                .execute()
            )
            logging.info(f"Event created: {event_result.get('htmlLink')}")
            return f"Event created: {event_result.get('htmlLink')}"

        except Exception as e:
            logging.info("Couldn't create an event")
            raise CustomException(e, sys)

    def search_calendar_event(
        self,
        event_name: str = None,
        time_min: str = None,
        max_result: int = 10,
        calendarID: str = "primary",
    ) -> str:
        if time_min is None:
            time_min = datetime.now(self.ist).isoformat()
        if time_min and "Z" not in time_min:
            try:
                dt_obj = datetime.fromisoformat(time_min)
                time_min = (
                    dt_obj.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
                )
            except ValueError:
                return "Invalid time_min format. Please provide a valid ISO 8601 date-time string."
        try:
            event_result = (
                self.service.events()
                .list(
                    calendarId=calendarID,
                    q=event_name,
                    timeMin=time_min,
                    maxResults=max_result,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

            events = event_result.get("items", [])
            if not events:
                logging.info("No matching events have found")
                return "No events found matching the criteria"
            event_details = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                event_details.append(
                    f"Event ID: {event['id']}\n"
                    f"Summary: {event.get('summary', 'No Title')}\n"
                    f"Start: {start}\n"
                    f"End: {end}\n"
                    f"Location: {event.get('location', 'N/A')}\n"
                    f"Description: {event.get('description', 'N/A')}\n"
                    f"Link: {event.get('htmlLink')}\n"
                    f"---"
                )
            logging.info("Found matching events in the list")
            return "\n".join(event_details)
        except Exception as e:
            logging.error(f"An error has occurred while searching for events: {e}")
            raise CustomException(e, sys)

    def delete_calendar_event(self, event_id: str, calendar_id: str = "primary") -> str:
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            logging.info(f"Event with ID {event_id} deleted successfully")
            return f"Event with ID {event_id} deleted successfully"
        except Exception as e:
            logging.error(f"An error has occurred: {e}")
            raise CustomException(e, sys)

    def list_calendar_event(
        self,
        time_min: str = None,
        time_max: str = None,
        max_result: int = 20,
        calendarID: str = "primary",
    ) -> str:
        if time_min is None:
            time_min = datetime.utcnow().isoformat() + "Z"

        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendarID,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_result,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            if not events:
                return "No events found in this calendar"

            all_event_details = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                all_event_details.append(
                    f"Event ID: {event['id']}\n"
                    f"Summary: {event.get('summary', 'No Title')}\n"
                    f"Start: {start}\n"
                    f"End: {end}\n"
                    f"Location: {event.get('location', 'N/A')}\n"
                    f"Description: {event.get('description', 'N/A')}\n"
                    f"Link: {event.get('htmlLink')}\n"
                    f"---"
                )
            return "\n".join(all_event_details)

        except Exception as e:
            logging.error(f"An error has occurred: {e}")
            raise CustomException(e, sys)
        