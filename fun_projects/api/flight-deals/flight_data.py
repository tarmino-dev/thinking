class FlightData:
    """This class is responsible for structuring the flight data."""

    def __init__(self, data):
        self.data = data
        self.cheapest_flight = self.find_cheapest_flight()
        if self.cheapest_flight:
            self.price = self.cheapest_flight["price"]["grandTotal"]
            self.departure = self.cheapest_flight["itineraries"][0]["segments"][0]["departure"]["iataCode"]
            self.arrival = self.cheapest_flight["itineraries"][0]["segments"][0]["arrival"]["iataCode"]
            self.departure_date = self.cheapest_flight["itineraries"][0]["segments"][0]["departure"]["at"].split("T")[
                0]
            self.write = True
        else:
            self.price = "N/A"
            self.departure = "N/A"
            self.arrival = "N/A"
            self.departure_date = "N/A"
            self.write = False

    def find_cheapest_flight(self):
        flights = self.data.get("data")
        if flights:
            cheapest_flight = flights[0]
            for flight in flights:
                if float(flight["price"]["grandTotal"]) < float(cheapest_flight["price"]["grandTotal"]):
                    cheapest_flight = flight
            return cheapest_flight
        else:
            return None
