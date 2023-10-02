package English;

import java.util.logging.Formatter;
import java.util.logging.LogRecord;

public class CustomFormatter extends Formatter {

    @Override
    public String format(LogRecord record) {

        StringBuilder builder = new StringBuilder();
        builder.append(formatMessage(record));

        return builder.toString();
    }
}

