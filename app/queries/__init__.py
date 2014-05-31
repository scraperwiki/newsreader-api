#!/usr/bin/env python
# encoding: utf-8

__all__ = ["properties_of_a_type"]

import queries

from .properties_of_a_type import properties_of_a_type
from .types_of_actors import types_of_actors
from .event_details_filtered_by_actor import event_details_filtered_by_actor
from .describe_uri import describe_uri
from .actors_of_a_type import actors_of_a_type
from .property_of_actors_of_a_type import property_of_actors_of_a_type
from .summary_of_events_with_actor import summary_of_events_with_actor
from .actors_sharing_event_with_an_actor import (
                                        actors_sharing_event_with_an_actor)

from .summary_of_events_with_two_actors import summary_of_events_with_two_actors

from .get_mention_metadata import get_mention_metadata
from .get_document import get_document