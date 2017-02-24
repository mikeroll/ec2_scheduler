# EC2 scheduler

A lightweight solution for starting/stoppping EC2 by cron schedule.
Depends on `boto` and `croniter`.

This is not expected to work out of the box, however it may.

### Configuration
Attach `autostate` tag to the instance with the value in format `is_enabled:start_cron:start_cron`, where `is_managed` is a true-ish value (see [here](ec2_scheduler.py#L50)) to have the instance state managed. `start_cron` and `stop_cron` should be valid cron expressions.

Example:
```
autostate = "Yes:5 * * * *:10 * * * *"
```

Attach `uri` tag with the value in format `subdomain_zone`, to have the instance's Route 53 record updated on instance state changes.

Example:
```
uri = "service_mycopr.example.com"
```

### Usage
Run the `ec2_scheduler.py` periodically wherever you like.
A good option would be AWS Lambda.
