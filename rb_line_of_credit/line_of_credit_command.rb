require_relative 'line_of_credit'
require 'date'

class String
  def is_number?
    true if Float(self) rescue false
  end
end

def parse_transaction_input(s)
  if s == 'done'
    return s
  else
    p = s.split(' ').map(&:strip)
    return [p[0]] + p[1, p.length].map(&:to_f)
  end
end

while true
  limit_input = ''
  until limit_input.is_number?
    puts "Please enter the principal for a new line of credit (Empty to quit)."
    limit_input = gets.chomp
    exit if limit_input == ''
  end
  limit = limit_input.to_f

  apr_input = ''
  until apr_input.is_number?
    puts "Please enter an APR, in % (e.g. for 35%, enter '35', not '0.35')"
    apr_input = gets.chomp
  end
  apr = apr_input.to_f

  x = LineOfCredit.new limit, apr

  transaction_input = ''
  until transaction_input == 'done'
    puts 'Please enter, separated by spaces:'
    puts '* A transaction type ("withdraw" or "pay")'
    puts '* A transaction amount'
    puts '* The number of days since the line of credit was opened (0 for same day)'
    puts 'Or, enter "done" to stop entering data.'
    transaction_input = parse_transaction_input(gets.chomp.downcase)

    if transaction_input != 'done'
      fn = x.method(transaction_input[0])
      fn.call(transaction_input[1], transaction_input[2])
      puts "Your current line of credit is #{x.principal} / #{x.limit}"
      puts "As of day 30, you will owe #{x.amount_owed}"
    end
  end
  puts "*** AMOUNT OWED ***"
  puts x.amount_owed
end