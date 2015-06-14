require 'awesome_print'
require 'date'
require 'set'

class LOCTransaction
  include Comparable
  def initialize(amount, date=Date.today)
    fail "You must enter an amount" if amount == 0
    raise "Date must be a valid date object" unless date.is_a? Date
    
    @amount = amount
    @date = date
  end

  attr_reader :amount
  attr_reader :date

  def <=>(another)
    return @date <=> another.date
  end
end

class LineOfCredit
  def initialize(limit, apr=35, opened_at=Date.today)
    raise "Limit must be a valid positive number." unless limit > 0.0
    raise "APR must be a positive number." unless apr > 0.0
    raise "Date must be a valid date object." unless opened_at.is_a? Date
    # we keep track of current principal in a variable because it's
    # significantly easier than calculating it every time we want
    # to use it.
    @limit = @principal = limit
    # frequently, APR is provided in percentage to make it easier to
    # read. let's make that assumption here.
    @apr = apr / 100.0 # this conveniently casts it as a float.
    @opened_at = Date.today
    @transactions = []
  end

  attr_reader :limit
  attr_reader :principal

  def owed
    return @limit - @principal
  end

  def add_transaction(amount, date=Date.today)
    date = @opened_at + date if date.is_a? Numeric # convert to date-type by assuming numbers = days
    fail "You cannot add a transaction before you opened your account!" if date < @opened_at
    
    # we're assuming here that transactions are monotonically increasing.
    fail "You cannot add a transaction for the past" if @transactions.length > 0 and date < @transactions.max.date
    
    # because of the above assumption this test is easy. if we could not assume
    # monotonically increasing transaction dates then the below would require re-calculation.
    fail "You cannot pay past your Line of Credit." if @principal + amount > @limit
    fail "You cannot withdraw more than your current balance." if @principal + amount < 0
    
    @principal += amount
    @transactions << LOCTransaction.new(amount, date)
  end

  alias pay add_transaction

  def withdraw(amount, date=Date.today)
    fail "You cannot withdraw more than you have!" if @principal - amount < 0
    add_transaction(-amount, date)
  end

  def amount_owed(period=1)
    raise "You must specify a positive period." unless period > 0
    as_of = @opened_at + (30 * period)

    # there are N calculations which must be performed, which
    # is the number of unique days across @opened_at + @transactions + 
    # as_of
    interest = 0.0
    current_date = @opened_at
    current_owed = 0
    
    # 1. iterate through transactions -- because of the assertion that
    # transactions are monotonically increasing we don't need to sort.
    # 2. package the edge between dates as a hash containing the amount
    # owed between the two dates and the number odays between the 2 dates.
    
    @transactions.sort.each do |transaction|
      break if transaction.date > as_of
      
      if transaction.date != current_date
        days = (transaction.date - current_date).floor
        if current_owed != 0
          interest += current_owed * @apr / 365 * days
        end
        current_date = transaction.date
      end
      current_owed -= transaction.amount
    end
    if current_date != as_of and current_owed
      days = as_of - current_date
      interest += current_owed * @apr / 365 * days
    end
    owed + (interest.round 2)
  end
end