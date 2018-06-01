"""
2RS Controller
"""
import logging
import gabby


class Controller(gabby.Gabby):
    """
    Class to controll all system operations and dispatch messages to
    the responsible modules
    """
    def transform(self, message):
        logging.info(f'Transforming data {message.data}')

        if message.belongs_to('processor_controller'):
            logging.info('Received message from processor')
            # return [gabby.Message(
            #     message.data,
            #     list(
            #         filter(
            #             lambda x : x.name == '2rs/viewer/input',
            #             self.output_topics)
            #         )
            #     )
            # ]
            return []

        elif message.belongs_to('receiver_controller'):
            logging.info('Received message from receiver')
            return [
                gabby.Message(
                    message.data[:18],
                    topics=self.get_topics('controller_processor')
                ),

                # gabby.Message(
                #     message.data[18:],
                #     topics=get_topics('controller_transmitter')
                # )
            ]

        return []

    def get_topics(self, alias):
        return list(
            filter(
                lambda x: x.alias == alias,
                [*self.output_topics, *self.input_topics]
            )
        )
