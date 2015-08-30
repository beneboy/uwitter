from .shared import notify_exchange, ProducerBase


class NotifyProducer(ProducerBase):
    def notify_of_post(self, poster, follower, post_content):
        self.put_message({'poster': poster, 'follower': follower, 'post_content': post_content}, notify_exchange)
