import com.sap.it.api.mapping.*;
import org.apache.commons.lang3.*;

/*
Create key attribute element value by adding zero(s) at the beginning of the value
until the desired passed length of it is achieved
*/

def String padLeftForNumeric(String value, int valueLength) {
    if (StringUtils.isEmpty(value)) {
        return ""
    }

    if (isNumeric(value)) {
        return padNumeric(value, valueLength)
    }

    return value
}

/*
Create key attribute element value by adding zero(s) at the beginning and whitespaces
at the end of the value until the desired length of it is achieved
*/

def String padLeftOrRightForAlphanumeric(String value, int valueLength) {
    if (StringUtils.isEmpty(value)) {
        return ""
    }

    if (isNumeric(value)) {
        return padNumeric(value, valueLength)
    }

    return value.padRight(valueLength)
}

/*
Create key attribute element value by adding whitespaces at the end of the value
until the desired length of it is achieved
*/

def String padRightForAlphanumeric(String value, int valueLength) {
    if (StringUtils.isEmpty(value)) {
        return ""
    }

    return value.padRight(valueLength)
}

def private boolean isNumeric(String value) {
    return value.matches("[0-9]+")
}

def private String padNumeric(String value, int valueLength) {
    return value.padLeft(valueLength, '0')
}
